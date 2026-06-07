from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RssSource:
    name: str
    feed_url: str


DEFAULT_RSS_SOURCES: list[RssSource] = [
    RssSource(name="연합뉴스 경제", feed_url="https://www.yna.co.kr/rss/economy.xml"),
    RssSource(name="매일경제 경제", feed_url="https://www.mk.co.kr/rss/30100041/"),
    RssSource(name="한국경제 증권", feed_url="https://www.hankyung.com/feed/finance"),
]

