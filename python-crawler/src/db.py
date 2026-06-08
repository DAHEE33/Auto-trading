from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extras import execute_values

from src.config import Settings
from src.models import NewsArticle, StockPriceSnapshot


@contextmanager
def get_connection(settings: Settings) -> Iterator:
    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
    try:
        yield conn
    finally:
        conn.close()


def save_articles(settings: Settings, articles: list[NewsArticle]) -> int:
    if not articles:
        return 0

    sql = """
        INSERT INTO news_article (title, url, source, published_at, content_summary)
        VALUES %s
        ON CONFLICT (url) DO NOTHING
    """
    rows = [
        (a.title, a.url, a.source, a.published_at, a.content_summary)
        for a in articles
    ]
    with get_connection(settings) as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
            inserted_count = cur.rowcount
        conn.commit()
    return inserted_count


def load_stocks(settings: Settings) -> list[tuple[int, str]]:
    sql = """
        SELECT id, ticker
        FROM stock
        WHERE ticker IS NOT NULL
          AND ticker <> ''
        ORDER BY id
    """
    with get_connection(settings) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    return [(int(row[0]), str(row[1])) for row in rows]


def save_stock_snapshots(settings: Settings, snapshots: list[StockPriceSnapshot]) -> int:
    if not snapshots:
        return 0

    sql = """
        INSERT INTO stock_price_snapshot (
            stock_id,
            base_date,
            close_price,
            change_rate_1d,
            change_rate_5d,
            change_rate_1m,
            volume_change_rate,
            drawdown_52w
        )
        VALUES %s
        ON CONFLICT (stock_id, base_date)
        DO UPDATE SET
            close_price = EXCLUDED.close_price,
            change_rate_1d = EXCLUDED.change_rate_1d,
            change_rate_5d = EXCLUDED.change_rate_5d,
            change_rate_1m = EXCLUDED.change_rate_1m,
            volume_change_rate = EXCLUDED.volume_change_rate,
            drawdown_52w = EXCLUDED.drawdown_52w,
            updated_at = NOW()
    """
    rows = [
        (
            s.stock_id,
            s.base_date,
            s.close_price,
            s.change_rate_1d,
            s.change_rate_5d,
            s.change_rate_1m,
            s.volume_change_rate,
            s.drawdown_52w,
        )
        for s in snapshots
    ]
    with get_connection(settings) as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
            affected_count = cur.rowcount
        conn.commit()
    return affected_count

