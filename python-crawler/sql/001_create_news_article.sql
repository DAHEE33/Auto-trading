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