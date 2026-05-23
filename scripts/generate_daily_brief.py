from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from market_brief.collector import collect_market_observations, today_kst
from market_brief.render import render_html
from market_brief.report import build_report


def main() -> int:
    args = parse_args()
    generated_on = date.fromisoformat(args.as_of_date) if args.as_of_date else today_kst()

    observations = collect_market_observations(
        as_of=generated_on,
        lookback_days=args.lookback_days,
    )
    report = build_report(observations, generated_on=generated_on)
    html = render_html(report)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dated_path = output_dir / f"{generated_on.isoformat()}.html"
    latest_path = output_dir / "latest.html"
    dated_path.write_text(html, encoding="utf-8")
    shutil.copyfile(dated_path, latest_path)

    print(f"Wrote {dated_path}")
    print(f"Wrote {latest_path}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the daily market brief HTML.")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "reports"),
        help="Directory where the generated HTML files are written.",
    )
    parser.add_argument(
        "--as-of-date",
        help="KST report date in YYYY-MM-DD. Defaults to today's date in Asia/Seoul.",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=21,
        help="Calendar days to request so holidays and weekends are covered.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
