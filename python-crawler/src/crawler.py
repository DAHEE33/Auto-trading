from __future__ import annotations

import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests

from src.config import Settings
from src.db import save_articles
from src.extractors import summarize_html
from src.models import NewsArticle
from src.rss_sources import DEFAULT_RSS_SOURCES, RssSource


logger = logging.getLogger(__name__)


def parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def collect_articles(settings: Settings, source: RssSource) -> list[NewsArticle]:
    feed = feedparser.parse(source.feed_url)
    articles: list[NewsArticle] = []

    for entry in feed.entries:
        url = getattr(entry, "link", "").strip()
        title = getattr(entry, "title", "").strip()
        published = parse_published_at(getattr(entry, "published", None))
        if not url or not title:
            continue

        try:
            response = requests.get(url, timeout=settings.crawl_timeout_seconds)
            response.raise_for_status()
            summary = summarize_html(response.text)
        except Exception as exc:
            logger.warning("본문 수집 실패 source=%s url=%s error=%s", source.name, url, exc)
            summary = ""

        if not summary:
            summary = getattr(entry, "summary", "").strip()[:500]
        if not summary:
            continue

        articles.append(
            NewsArticle(
                title=title[:500],
                url=url[:2000],
                source=source.name,
                published_at=published,
                content_summary=summary,
            )
        )
    return articles


def run_once(settings: Settings) -> dict[str, int]:
    total_collected = 0
    total_inserted = 0
    for source in DEFAULT_RSS_SOURCES:
        try:
            articles = collect_articles(settings, source)
            inserted = save_articles(settings, articles)
            total_collected += len(articles)
            total_inserted += inserted
            logger.info(
                "크롤링 완료 source=%s collected=%d inserted=%d",
                source.name,
                len(articles),
                inserted,
            )
        except Exception as exc:
            logger.exception("크롤링 실패 source=%s error=%s", source.name, exc)

    return {
        "collected": total_collected,
        "inserted": total_inserted,
    }

