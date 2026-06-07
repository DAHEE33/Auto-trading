from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extras import execute_values

from src.config import Settings
from src.models import NewsArticle


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

