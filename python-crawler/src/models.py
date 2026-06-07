from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewsArticle:
    title: str
    url: str
    source: str
    published_at: datetime | None
    content_summary: str

