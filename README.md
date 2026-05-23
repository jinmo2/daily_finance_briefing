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

### 수동 테스트 실행

GitHub Actions의 `Daily Market Brief` 워크플로를 수동 실행할 때 `target_date`를 `YYYY-MM-DD` 형식으로 입력하면 해당 날짜 데이터를 기준으로 리포트를 생성합니다.

예: `target_date=2026-05-22`
