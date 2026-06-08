from __future__ import annotations

import logging
import signal

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.config import Settings
from src.crawler import run_once
from src.stock_crawler import run_stock_once


logger = logging.getLogger(__name__)


def start_scheduler(settings: Settings) -> None:
    scheduler = BlockingScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        func=lambda: run_once(settings),
        trigger=IntervalTrigger(minutes=settings.crawl_interval_minutes),
        id="rss_news_crawl",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    def shutdown_handler(signum, frame):  # type: ignore[no-untyped-def]
        logger.info("스케줄러 종료 시그널 수신 signum=%s", signum)
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info(
        "뉴스 크롤러 스케줄러 시작 interval=%d분",
        settings.crawl_interval_minutes,
    )
    run_once(settings)
    scheduler.start()


def start_stock_scheduler(settings: Settings) -> None:
    scheduler = BlockingScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        func=lambda: run_stock_once(settings),
        trigger=CronTrigger(
            day_of_week="mon-fri",
            hour=settings.stock_schedule_hour,
            minute=settings.stock_schedule_minute,
        ),
        id="stock_price_snapshot",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    def shutdown_handler(signum, frame):  # type: ignore[no-untyped-def]
        logger.info("주가 스케줄러 종료 시그널 수신 signum=%s", signum)
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info(
        "주가 스케줄러 시작 실행시각=평일 %02d:%02d",
        settings.stock_schedule_hour,
        settings.stock_schedule_minute,
    )
    scheduler.start()

