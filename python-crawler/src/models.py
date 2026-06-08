from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class NewsArticle:
    title: str
    url: str
    source: str
    published_at: datetime | None
    content_summary: str


@dataclass(frozen=True)
class StockPriceSnapshot:
    stock_id: int
    base_date: date
    close_price: float
    change_rate_1d: float | None
    change_rate_5d: float | None
    change_rate_1m: float | None
    volume_change_rate: float | None
    drawdown_52w: float | None

