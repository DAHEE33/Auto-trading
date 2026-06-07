from __future__ import annotations

import logging
import signal

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config import Settings
from src.crawler import run_once


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

