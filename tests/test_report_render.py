from __future__ import annotations

from datetime import date

from market_brief.collector import MarketObservation
from market_brief.render import render_html
from market_brief.report import build_report, format_signed_percent, trend_css_class


def test_format_signed_percent() -> None:
    assert format_signed_percent(1.234) == "+1.23%"
    assert format_signed_percent(-1.234) == "-1.23%"
    assert format_signed_percent(0) == "0.00%"
    assert format_signed_percent(None) == "-"


def test_trend_css_class() -> None:
    assert trend_css_class(10) == "trend-up"
    assert trend_css_class(-10) == "trend-down"
    assert trend_css_class(0) == "trend-flat"
    assert trend_css_class(None) == "trend-flat"


def test_render_html_contains_sections_and_rows() -> None:
    observations = [
        MarketObservation(
            category="국내증시",
            name="코스피",
            symbol="KS11",
            note="종합지수",
            value=2700.12,
            previous_value=2680.12,
            change=20.0,
            change_pct=0.746,
            observed_on=date(2026, 5, 22),
            status="ok",
        ),
        MarketObservation(
            category="상품",
            name="WTI",
            symbol="CL=F",
            note="선물 가격",
            value=None,
            previous_value=None,
            change=None,
            change_pct=None,
            observed_on=None,
            status="error",
            error="temporary failure",
        ),
    ]

    html = render_html(build_report(observations, generated_on=date(2026, 5, 23)))

    assert "전일 시장 요약" in html
    assert "국내증시" in html
    assert "category-domestic" in html
    assert "상품" in html
    assert "category-commodity" in html
    assert "코스피" in html
    assert "2,700.12" in html
    assert "+0.75%" in html
    assert "데이터 없음" in html
    assert "temporary failure" in html
