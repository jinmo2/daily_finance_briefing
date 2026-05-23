from __future__ import annotations

from html import escape

from market_brief.report import DisplayRow, MarketReport


def render_html(report: MarketReport) -> str:
    sections = "\n".join(
        _render_section(category, rows)
        for category, rows in report.rows_by_category.items()
    )
    generated_on = escape(report.generated_on.isoformat())
    title = escape(report.title)

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - {generated_on}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --line: #d9dee7;
      --text: #1f2937;
      --muted: #667085;
      --up: #c2410c;
      --down: #1d4ed8;
      --flat: #475467;
      --header: #263241;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", sans-serif;
      line-height: 1.5;
    }}
    main {{
      width: min(1080px, calc(100% - 32px));
      margin: 32px auto;
    }}
    header {{
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 6px;
      color: var(--header);
      font-size: 30px;
      font-weight: 800;
      letter-spacing: 0;
    }}
    .meta {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    section {{
      margin: 22px 0;
    }}
    h2 {{
      margin: 0 0 10px;
      color: var(--header);
      font-size: 18px;
      font-weight: 750;
      letter-spacing: 0;
    }}
    .category-label {{
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      padding: 3px 10px;
      border-radius: 8px;
      border: 1px solid currentColor;
      background: #ffffff;
      font-weight: 800;
    }}
    .category-domestic {{
      color: #b42318;
      background: #fff4ed;
    }}
    .category-overseas {{
      color: #175cd3;
      background: #eff8ff;
    }}
    .category-exchange {{
      color: #067647;
      background: #ecfdf3;
    }}
    .category-commodity {{
      color: #b54708;
      background: #fffaeb;
    }}
    .category-default {{
      color: #475467;
      background: #f9fafb;
    }}
    .table-wrap {{
      overflow-x: auto;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: right;
      white-space: nowrap;
      font-size: 14px;
    }}
    th {{
      background: #eef2f7;
      color: #344054;
      font-weight: 700;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    th:first-child, td:first-child,
    th:nth-child(2), td:nth-child(2) {{
      text-align: left;
    }}
    .name {{
      font-weight: 700;
    }}
    .symbol {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 500;
    }}
    .trend-up {{
      color: var(--up);
      font-weight: 750;
    }}
    .trend-down {{
      color: var(--down);
      font-weight: 750;
    }}
    .trend-flat {{
      color: var(--flat);
      font-weight: 650;
    }}
    .error {{
      color: var(--muted);
      font-size: 12px;
      white-space: normal;
    }}
    footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 640px) {{
      main {{
        width: min(100% - 20px, 1080px);
        margin: 20px auto;
      }}
      h1 {{
        font-size: 24px;
      }}
      th, td {{
        padding: 10px 12px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{title}</h1>
      <p class="meta">생성일: {generated_on} · 각 항목은 가장 최근 유효 거래일 기준입니다.</p>
    </header>
{sections}
    <footer>
      데이터 출처: FinanceDataReader. 환율은 1달러당 상대 통화 기준이며, 상품은 선물 가격 기준입니다.
    </footer>
  </main>
</body>
</html>
"""


def _render_section(category: str, rows: list[DisplayRow]) -> str:
    body = "\n".join(_render_row(row) for row in rows)
    category_class = _category_class(category)
    return f"""    <section>
      <h2><span class="category-label {category_class}">{escape(category)}</span></h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>설명</th>
              <th>현재값</th>
              <th>등락</th>
              <th>등락률</th>
              <th>기준일</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
{body}
          </tbody>
        </table>
      </div>
    </section>"""


def _render_row(row: DisplayRow) -> str:
    status = "정상" if row.status == "ok" else "확인 필요"
    if row.error:
        status = f'{status}<span class="error">{escape(row.error)}</span>'

    return f"""            <tr>
              <td><span class="name">{escape(row.name)}</span><span class="symbol">{escape(row.symbol)}</span></td>
              <td>{escape(row.note)}</td>
              <td>{escape(row.value)}</td>
              <td class="{escape(row.trend_class)}">{escape(row.change)}</td>
              <td class="{escape(row.trend_class)}">{escape(row.change_pct)}</td>
              <td>{escape(row.observed_on)}</td>
              <td>{status}</td>
            </tr>"""


def _category_class(category: str) -> str:
    classes = {
        "국내증시": "category-domestic",
        "해외증시": "category-overseas",
        "환율": "category-exchange",
        "상품": "category-commodity",
    }
    return classes.get(category, "category-default")
