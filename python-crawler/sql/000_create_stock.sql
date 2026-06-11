CREATE TABLE IF NOT EXISTS stock (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200),
    market VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ticker: FinanceDataReader에서 조회 가능한 종목 식별자
-- 한국: 005930, 000660 같은 코드
-- 미국: AAPL, MSFT 같은 심볼
--market: 현재는 자유 텍스트라 KOSPI, KOSDAQ, NASDAQ, NYSE 등으로 운영 규칙 정하면 됩니다.

CREATE INDEX IF NOT EXISTS idx_stock_ticker
    ON stock (ticker);

    
INSERT INTO stock (ticker, name, market)
VALUES
    ('005930', '삼성전자', 'KOSPI'),
    ('000660', 'SK하이닉스', 'KOSPI')
ON CONFLICT (ticker) DO NOTHING;

SELECT s.ticker, p.base_date, p.close_price, p.change_rate_1d, p.change_rate_5d, p.change_rate_1m, p.volume_change_rate, p.drawdown_52w
FROM stock_price_snapshot p
         JOIN stock s ON s.id = p.stock_id
ORDER BY p.base_date DESC, s.ticker
LIMIT 20;

-- 신규 상장/데이터 부족 검증 SQL
SELECT s.ticker, p.base_date, p.drawdown_52w, p.change_rate_1m
FROM stock_price_snapshot p
JOIN stock s ON s.id = p.stock_id
WHERE p.drawdown_52w IS NULL
ORDER BY p.base_date DESC
LIMIT 20;

-- 중복 확인 SQL
SELECT stock_id, base_date, COUNT(*)
FROM stock_price_snapshot
GROUP BY stock_id, base_date
HAVING COUNT(*) > 1;
