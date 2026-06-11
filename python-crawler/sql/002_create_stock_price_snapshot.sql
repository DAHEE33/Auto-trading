CREATE TABLE IF NOT EXISTS stock_price_snapshot (
    id BIGSERIAL PRIMARY KEY,
    stock_id BIGINT NOT NULL REFERENCES stock(id),
    base_date DATE NOT NULL,
    close_price NUMERIC(14, 2) NOT NULL,
    change_rate_1d NUMERIC(10, 4),
    change_rate_5d NUMERIC(10, 4),
    change_rate_1m NUMERIC(10, 4),
    volume_change_rate NUMERIC(10, 4),
    drawdown_52w NUMERIC(10, 4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_stock_price_snapshot_stock_date UNIQUE (stock_id, base_date)
);

CREATE INDEX IF NOT EXISTS idx_stock_price_snapshot_base_date
    ON stock_price_snapshot (base_date DESC);

CREATE INDEX IF NOT EXISTS idx_stock_price_snapshot_stock_id
    ON stock_price_snapshot (stock_id);


-- Migration: 1개월(명칭) -> 21거래일(명칭) 정합화
ALTER TABLE stock_price_snapshot
    RENAME COLUMN change_rate_1m TO change_rate_21d;    

-- 이미 DB있는 곳에서 변경경
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'stock_price_snapshot'
          AND column_name = 'change_rate_1m'
    ) THEN
        EXECUTE 'ALTER TABLE stock_price_snapshot RENAME COLUMN change_rate_1m TO change_rate_21d';
    END IF;
END $$;    
