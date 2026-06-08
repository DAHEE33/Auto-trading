from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib import robotparser
from urllib.parse import urlparse

import feedparser
import requests

from src.config import Settings
from src.db import save_articles
from src.extractors import summarize_html
from src.models import NewsArticle
from src.rss_sources import DEFAULT_RSS_SOURCES, RssSource


logger = logging.getLogger(__name__)


class RobotsChecker:
    def __init__(self, user_agent: str = "*") -> None:
        self.user_agent = user_agent
        self._parsers: dict[str, robotparser.RobotFileParser] = {}

    def can_fetch(self, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = self._parsers.get(robots_url)
        if parser is None:
            parser = robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception as exc:
                logger.warning("robots.txt 조회 실패 robots=%s error=%s", robots_url, exc)
                return True
            self._parsers[robots_url] = parser

        allowed = parser.can_fetch(self.user_agent, url)
        if not allowed:
            logger.info("robots.txt 차단으로 스킵 url=%s", url)
        return allowed


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
    robots_checker = RobotsChecker()
    last_request_at = 0.0

    for entry in feed.entries:
        url = getattr(entry, "link", "").strip()
        title = getattr(entry, "title", "").strip()
        published = parse_published_at(getattr(entry, "published", None))
        if not url or not title:
            continue
        if not robots_checker.can_fetch(url):
            continue

        try:
            elapsed = time.monotonic() - last_request_at
            wait_seconds = settings.crawl_request_delay_seconds - elapsed
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            last_request_at = time.monotonic()
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

