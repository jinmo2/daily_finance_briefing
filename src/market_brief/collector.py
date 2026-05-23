from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo


DataReader = Callable[[str, str, str], Any]


@dataclass(frozen=True)
class Instrument:
    category: str
    name: str
    symbol: str
    note: str


@dataclass(frozen=True)
class MarketObservation:
    category: str
    name: str
    symbol: str
    note: str
    value: float | None
    previous_value: float | None
    change: float | None
    change_pct: float | None
    observed_on: date | None
    status: str
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.status == "ok"


DEFAULT_INSTRUMENTS: tuple[Instrument, ...] = (
    Instrument("국내증시", "코스피", "KS11", "종합지수"),
    Instrument("국내증시", "코스닥", "KQ11", "종합지수"),
    Instrument("해외증시", "다우산업", "DJI", "종합지수"),
    Instrument("해외증시", "나스닥 종합", "IXIC", "종합지수"),
    Instrument("해외증시", "상해종합", "SSEC", "종합지수"),
    Instrument("해외증시", "니케이225", "N225", "종합지수"),
    Instrument("환율", "원/달러", "USD/KRW", "1 USD당 KRW"),
    Instrument("환율", "중국위안/달러", "USD/CNY", "1 USD당 CNY"),
    Instrument("환율", "엔화/달러", "USD/JPY", "1 USD당 JPY"),
    Instrument("상품", "금", "GC=F", "선물 가격"),
    Instrument("상품", "은", "SI=F", "선물 가격"),
    Instrument("상품", "WTI", "CL=F", "선물 가격"),
)


def today_kst() -> date:
    return datetime.now(ZoneInfo("Asia/Seoul")).date()


def collect_market_observations(
    instruments: Sequence[Instrument] = DEFAULT_INSTRUMENTS,
    *,
    as_of: date | None = None,
    lookback_days: int = 21,
    data_reader: DataReader | None = None,
) -> list[MarketObservation]:
    """Fetch recent prices and calculate the latest daily change per instrument."""

    if lookback_days < 2:
        raise ValueError("lookback_days must be at least 2")

    reader = data_reader or _load_finance_data_reader()
    report_date = as_of or today_kst()
    end_date = report_date - timedelta(days=1)
    start_date = end_date - timedelta(days=lookback_days)

    observations: list[MarketObservation] = []
    for instrument in instruments:
        observations.append(
            _collect_one(
                instrument,
                reader=reader,
                start_date=start_date,
                end_date=end_date,
            )
        )
    return observations


def _load_finance_data_reader() -> DataReader:
    try:
        import FinanceDataReader as fdr
    except ImportError as exc:
        raise RuntimeError(
            "FinanceDataReader is not installed. Run `python -m pip install -e .`."
        ) from exc

    return fdr.DataReader


def _collect_one(
    instrument: Instrument,
    *,
    reader: DataReader,
    start_date: date,
    end_date: date,
) -> MarketObservation:
    try:
        frame = reader(
            instrument.symbol,
            start_date.isoformat(),
            end_date.isoformat(),
        )
        latest, previous = _latest_two_closes(frame)
        if latest is None:
            return _failed(instrument, "유효한 종가 데이터가 없습니다.")

        latest_date, latest_value = latest
        if previous is None:
            return MarketObservation(
                category=instrument.category,
                name=instrument.name,
                symbol=instrument.symbol,
                note=instrument.note,
                value=latest_value,
                previous_value=None,
                change=None,
                change_pct=None,
                observed_on=latest_date,
                status="partial",
                error="직전 거래일 데이터가 없습니다.",
            )

        _, previous_value = previous
        change = latest_value - previous_value
        change_pct = None if previous_value == 0 else (change / previous_value) * 100
        return MarketObservation(
            category=instrument.category,
            name=instrument.name,
            symbol=instrument.symbol,
            note=instrument.note,
            value=latest_value,
            previous_value=previous_value,
            change=change,
            change_pct=change_pct,
            observed_on=latest_date,
            status="ok",
        )
    except Exception as exc:  # FinanceDataReader uses multiple upstream crawlers.
        return _failed(instrument, str(exc))


def _latest_two_closes(frame: Any) -> tuple[tuple[date, float] | None, tuple[date, float] | None]:
    if frame is None or getattr(frame, "empty", True):
        return None, None

    close_column = _find_close_column(frame)
    if close_column is None:
        raise ValueError("Close column not found")

    series = frame[close_column].dropna().sort_index()
    if series.empty:
        return None, None

    latest_date = _index_value_to_date(series.index[-1])
    latest_value = float(series.iloc[-1])
    latest = (latest_date, latest_value)

    if len(series) < 2:
        return latest, None

    previous_date = _index_value_to_date(series.index[-2])
    previous_value = float(series.iloc[-2])
    return latest, (previous_date, previous_value)


def _find_close_column(frame: Any) -> str | None:
    for column in getattr(frame, "columns", []):
        if str(column).lower() == "close":
            return str(column)
    return None


def _index_value_to_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if hasattr(value, "date"):
        return value.date()
    return datetime.fromisoformat(str(value)).date()


def _failed(instrument: Instrument, message: str) -> MarketObservation:
    return MarketObservation(
        category=instrument.category,
        name=instrument.name,
        symbol=instrument.symbol,
        note=instrument.note,
        value=None,
        previous_value=None,
        change=None,
        change_pct=None,
        observed_on=None,
        status="error",
        error=message,
    )
