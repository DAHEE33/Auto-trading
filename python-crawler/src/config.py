from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default))
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer. current={value}") from exc


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name, str(default))
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number. current={value}") from exc


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = _get_int("DB_PORT", 5432)
    db_name: str = os.getenv("DB_NAME", "marketlens")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    crawl_interval_minutes: int = _get_int("CRAWL_INTERVAL_MINUTES", 30)
    crawl_timeout_seconds: int = _get_int("CRAWL_TIMEOUT_SECONDS", 10)
    crawl_request_delay_seconds: float = max(1.0, _get_float("CRAWL_REQUEST_DELAY_SECONDS", 1.0))
    stock_schedule_hour: int = _get_int("STOCK_SCHEDULE_HOUR", 8)
    stock_schedule_minute: int = _get_int("STOCK_SCHEDULE_MINUTE", 30)
    stock_lookback_days: int = _get_int("STOCK_LOOKBACK_DAYS", 400)
    stock_volume_avg_days: int = _get_int("STOCK_VOLUME_AVG_DAYS", 20)

