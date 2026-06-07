from __future__ import annotations

import argparse
import logging

from src.config import Settings
from src.crawler import run_once
from src.scheduler import start_scheduler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 1 STEP 1-1 뉴스 크롤러")
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
        result = run_once(settings)
        logging.info("1회 실행 완료 collected=%d inserted=%d", result["collected"], result["inserted"])
        return

    start_scheduler(settings)


if __name__ == "__main__":
    main()

