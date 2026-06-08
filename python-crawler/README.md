# Phase 1 STEP 1-1/1-2: 데이터 수집기

## 포함 범위
- RSS 기반 경제 뉴스 수집
- 원문 HTML 본문 요약 추출
- URL 기반 중복 제거 저장
- 주기 실행 스케줄러
- FinanceDataReader 기반 주가 데이터 수집
- 주가 지표 계산 (1일/5일/1개월 등락률, 거래량 배율, 52주 드로우다운)
- `stock_price_snapshot` 저장

## 디렉터리 구조
```text
python-crawler/
├─ requirements.txt
├─ .env.example
├─ sql/
│  └─ 000_create_stock.sql
│  └─ 001_create_news_article.sql
│  └─ 002_create_stock_price_snapshot.sql
└─ src/
   ├─ main.py
   ├─ scheduler.py
   ├─ crawler.py
   ├─ stock_crawler.py
   ├─ db.py
   ├─ extractors.py
   ├─ rss_sources.py
   ├─ models.py
   └─ config.py
```

## 설치
```bash
cd python-crawler
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 환경 변수 설정
1. `.env.example`을 `.env`로 복사
2. DB 연결 정보 입력

필수 키:
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

옵션:
- `CRAWL_INTERVAL_MINUTES` (기본 30)
- `CRAWL_TIMEOUT_SECONDS` (기본 10)
- `CRAWL_REQUEST_DELAY_SECONDS` (기본 1.0, 최소 1초)
- `STOCK_SCHEDULE_HOUR` (기본 8)
- `STOCK_SCHEDULE_MINUTE` (기본 30)
- `STOCK_LOOKBACK_DAYS` (기본 400)
- `STOCK_VOLUME_AVG_DAYS` (기본 20)

## DB 스키마 적용
아래 순서로 실행:
1. `sql/000_create_stock.sql`
2. `sql/001_create_news_article.sql`
3. `sql/002_create_stock_price_snapshot.sql`

`stock` 마스터 데이터 예시:
```sql
INSERT INTO stock (ticker, name, market)
VALUES
    ('005930', '삼성전자', 'KOSPI'),
    ('000660', 'SK하이닉스', 'KOSPI')
ON CONFLICT (ticker) DO NOTHING;
```

## 실행
### 1회 실행
```bash
python -m src.main --job news --once
python -m src.main --job stock --once
```

### 스케줄러 실행
```bash
python -m src.main --job news
python -m src.main --job stock
```

## 크롤링 정책
- 기사 원문 요청 전 `robots.txt` 허용 여부를 확인합니다.
- 기사 원문 요청은 `CRAWL_REQUEST_DELAY_SECONDS` 기준으로 최소 1초 간격을 유지합니다.

## 검증 쿼리
```sql
SELECT id, source, title, url, published_at, created_at
FROM news_article
ORDER BY created_at DESC
LIMIT 20;
```

중복 URL 확인:
```sql
SELECT url, COUNT(*) AS cnt
FROM news_article
GROUP BY url
HAVING COUNT(*) > 1;
```

주가 스냅샷 확인:
```sql
SELECT s.ticker, p.base_date, p.close_price, p.change_rate_1d, p.change_rate_5d, p.change_rate_1m, p.volume_change_rate, p.drawdown_52w
FROM stock_price_snapshot p
JOIN stock s ON s.id = p.stock_id
ORDER BY p.base_date DESC, s.ticker
LIMIT 20;
```

