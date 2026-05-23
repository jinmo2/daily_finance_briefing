"""Daily market brief generation package."""

from market_brief.collector import Instrument, MarketObservation, collect_market_observations
from market_brief.report import build_report
from market_brief.render import render_html

__all__ = [
    "Instrument",
    "MarketObservation",
    "build_report",
    "collect_market_observations",
    "render_html",
]
