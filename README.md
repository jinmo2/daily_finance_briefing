# Daily Market Brief

FinanceDataReader로 주요 증시, 환율, 상품 가격을 조회해 `전일 시장 요약` HTML을 생성합니다.

## 로컬 실행

```powershell
python -m pip install -e ".[dev]"
python scripts/generate_daily_brief.py
```

생성 결과:

- `reports/YYYY-MM-DD.html`
- `reports/latest.html`

## GitHub Actions

`.github/workflows/daily-brief.yml`은 매일 `00:00 UTC`에 실행됩니다. 한국시간 기준으로는 오전 09시입니다.

워크플로는 HTML을 생성한 뒤 변경된 `reports/` 파일을 저장소에 커밋합니다.
