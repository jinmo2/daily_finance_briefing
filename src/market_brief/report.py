from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from market_brief.collector import MarketObservation


CATEGORY_ORDER = ("국내증시", "해외증시", "환율", "상품")


@dataclass(frozen=True)
class DisplayRow:
    category: str
    name: str
    symbol: str
    note: str
    value: str
    change: str
    change_pct: str
    observed_on: str
    trend_class: str
    status: str
    error: str | None


@dataclass(frozen=True)
class MarketReport:
    title: str
    generated_on: date
    rows_by_category: dict[str, list[DisplayRow]]


def build_report(observations: list[MarketObservation], *, generated_on: date) -> MarketReport:
    grouped: dict[str, list[DisplayRow]] = defaultdict(list)
    for observation in observations:
        grouped[observation.category].append(to_display_row(observation))

    ordered = {
        category: grouped.get(category, [])
        for category in CATEGORY_ORDER
        if category in grouped
    }
    for category, rows in grouped.items():
        if category not in ordered:
            ordered[category] = rows

    return MarketReport(
        title="전일 시장 요약",
        generated_on=generated_on,
        rows_by_category=ordered,
    )


def to_display_row(observation: MarketObservation) -> DisplayRow:
    trend_class = trend_css_class(observation.change)
    return DisplayRow(
        category=observation.category,
        name=observation.name,
        symbol=observation.symbol,
        note=observation.note,
        value=format_number(observation.value) if observation.value is not None else "데이터 없음",
        change=format_signed_number(observation.change),
        change_pct=format_signed_percent(observation.change_pct),
        observed_on=observation.observed_on.isoformat() if observation.observed_on else "-",
        trend_class=trend_class,
        status=observation.status,
        error=observation.error,
    )


def trend_css_class(change: float | None) -> str:
    if change is None:
        return "trend-flat"
    if change > 0:
        return "trend-up"
    if change < 0:
        return "trend-down"
    return "trend-flat"


def format_number(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:,.2f}"


def format_signed_number(value: float | None) -> str:
    if value is None:
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:,.2f}"


def format_signed_percent(value: float | None) -> str:
    if value is None:
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"
