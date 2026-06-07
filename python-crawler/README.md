# Phase 1 STEP 1-1: 뉴스 크롤러

## 포함 범위
- RSS 기반 경제 뉴스 수집
- 원문 HTML 본문 요약 추출
- URL 기반 중복 제거 저장
- 주기 실행 스케줄러

## 디렉터리 구조
```text
python-crawler/
├─ requirements.txt
├─ .env.example
├─ sql/
│  └─ 001_create_news_article.sql
└─ src/
   ├─ main.py
   ├─ scheduler.py
   ├─ crawler.py
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

## DB 스키마 적용
`sql/001_create_news_article.sql` 실행

## 실행
### 1회 실행
```bash
python -m src.main --once
```

### 스케줄러 실행
```bash
python -m src.main
```

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

