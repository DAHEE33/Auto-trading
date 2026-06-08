from __future__ import annotations

import logging
from datetime import datetime, timedelta

import FinanceDataReader as fdr
import pandas as pd

from src.config import Settings
from src.db import load_stocks, save_stock_snapshots
from src.models import StockPriceSnapshot


logger = logging.getLogger(__name__)


def _to_float(value: float | int | None) -> float | None:
    if value is None:
        return None
    if pd.isna(value):
        return None
    return float(value)


def _calc_change_rate(base_close: float, previous_close: float | None) -> float | None:
    if previous_close is None or previous_close == 0:
        return None
    return ((base_close / previous_close) - 1.0) * 100.0


def _build_snapshot(
    stock_id: int,
    ticker: str,
    frame: pd.DataFrame,
    volume_avg_days: int,
) -> StockPriceSnapshot | None:
    if frame.empty:
        return None

    data = frame.copy()
    data = data.sort_index()
    data["Close"] = pd.to_numeric(data["Close"], errors="coerce")
    data["Volume"] = pd.to_numeric(data["Volume"], errors="coerce")
    data = data.dropna(subset=["Close", "Volume"])
    data = data[data["Close"] > 0]
    if data.empty:
        return None

    data["close_shift_1"] = data["Close"].shift(1)
    data["close_shift_5"] = data["Close"].shift(5)
    data["close_shift_21"] = data["Close"].shift(21)
    data["rolling_high_252"] = data["Close"].rolling(window=252, min_periods=1).max()
    data["volume_avg"] = data["Volume"].rolling(window=volume_avg_days, min_periods=1).mean()

    base = data.iloc[-1]
    base_close = float(base["Close"])
    base_date = data.index[-1].date()

    change_rate_1d = _calc_change_rate(base_close, _to_float(base["close_shift_1"]))
    change_rate_5d = _calc_change_rate(base_close, _to_float(base["close_shift_5"]))
    change_rate_1m = _calc_change_rate(base_close, _to_float(base["close_shift_21"]))

    rolling_high_252 = _to_float(base["rolling_high_252"])
    drawdown_52w = None
    if rolling_high_252 and rolling_high_252 > 0:
        drawdown_52w = ((base_close / rolling_high_252) - 1.0) * 100.0

    volume_avg = _to_float(base["volume_avg"])
    volume_change_rate = None
    if volume_avg and volume_avg > 0:
        volume_change_rate = float(base["Volume"]) / volume_avg

    snapshot = StockPriceSnapshot(
        stock_id=stock_id,
        base_date=base_date,
        close_price=base_close,
        change_rate_1d=change_rate_1d,
        change_rate_5d=change_rate_5d,
        change_rate_1m=change_rate_1m,
        volume_change_rate=volume_change_rate,
        drawdown_52w=drawdown_52w,
    )
    logger.debug("스냅샷 계산 완료 ticker=%s date=%s", ticker, base_date.isoformat())
    return snapshot


def run_stock_once(settings: Settings) -> dict[str, int]:
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=settings.stock_lookback_days)
    stocks = load_stocks(settings)
    snapshots: list[StockPriceSnapshot] = []
    failed_count = 0

    for stock_id, ticker in stocks:
        try:
            frame = fdr.DataReader(ticker, start_date, end_date)
            snapshot = _build_snapshot(
                stock_id=stock_id,
                ticker=ticker,
                frame=frame,
                volume_avg_days=settings.stock_volume_avg_days,
            )
            if snapshot is None:
                logger.warning("주가 데이터 없음 ticker=%s", ticker)
                continue
            snapshots.append(snapshot)
        except Exception as exc:
            failed_count += 1
            logger.exception("주가 수집 실패 ticker=%s error=%s", ticker, exc)

    affected = save_stock_snapshots(settings, snapshots)
    logger.info(
        "주가 수집 완료 stocks=%d snapshots=%d affected=%d failed=%d",
        len(stocks),
        len(snapshots),
        affected,
        failed_count,
    )
    return {
        "stocks": len(stocks),
        "snapshots": len(snapshots),
        "affected": affected,
        "failed": failed_count,
    }
