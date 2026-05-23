from __future__ import annotations

from datetime import date

import pandas as pd

from market_brief.collector import Instrument, collect_market_observations


INSTRUMENT = Instrument("테스트", "테스트지수", "TEST", "테스트")


def test_collect_market_observations_calculates_latest_change() -> None:
    frame = pd.DataFrame(
        {"Close": [100.0, 110.0, 104.5]},
        index=pd.to_datetime(["2026-05-20", "2026-05-21", "2026-05-22"]),
    )
    calls = []

    rows = collect_market_observations(
        [INSTRUMENT],
        as_of=date(2026, 5, 23),
        data_reader=lambda symbol, start, end: calls.append((symbol, start, end)) or frame,
    )

    row = rows[0]
    assert row.status == "ok"
    assert row.value == 104.5
    assert row.previous_value == 110.0
    assert row.change == -5.5
    assert round(row.change_pct or 0, 2) == -5.0
    assert row.observed_on == date(2026, 5, 22)
    assert calls == [("TEST", "2026-05-01", "2026-05-22")]


def test_collect_market_observations_handles_empty_data() -> None:
    frame = pd.DataFrame({"Close": []})

    rows = collect_market_observations(
        [INSTRUMENT],
        as_of=date(2026, 5, 23),
        data_reader=lambda symbol, start, end: frame,
    )

    assert rows[0].status == "error"
    assert rows[0].value is None
    assert "종가" in (rows[0].error or "")


def test_collect_market_observations_handles_single_valid_close() -> None:
    frame = pd.DataFrame(
        {"Close": [123.45]},
        index=pd.to_datetime(["2026-05-22"]),
    )

    rows = collect_market_observations(
        [INSTRUMENT],
        as_of=date(2026, 5, 23),
        data_reader=lambda symbol, start, end: frame,
    )

    assert rows[0].status == "partial"
    assert rows[0].value == 123.45
    assert rows[0].change_pct is None
    assert rows[0].observed_on == date(2026, 5, 22)
