from __future__ import annotations

import argparse
import logging

from src.config import Settings
from src.crawler import run_once
from src.scheduler import start_scheduler, start_stock_scheduler
from src.stock_crawler import run_stock_once


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 1 데이터 수집기")
    parser.add_argument(
        "--job",
        choices=["news", "stock"],
        default="news",
        help="실행할 작업 유형 (기본: news)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="1회 실행 후 종료",
    )
    return parser


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    args = build_parser().parse_args()
    settings = Settings()

    if args.once:
        if args.job == "news":
            result = run_once(settings)
            logging.info("뉴스 1회 실행 완료 collected=%d inserted=%d", result["collected"], result["inserted"])
        else:
            result = run_stock_once(settings)
            logging.info(
                "주가 1회 실행 완료 stocks=%d snapshots=%d affected=%d failed=%d",
                result["stocks"],
                result["snapshots"],
                result["affected"],
                result["failed"],
            )
        return

    if args.job == "news":
        start_scheduler(settings)
    else:
        start_stock_scheduler(settings)


if __name__ == "__main__":
    main()

