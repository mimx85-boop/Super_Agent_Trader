from ib_insync import IB, Stock, util
import pandas as pd
import pandas as _pd
import numpy as _np
from datetime import datetime, timedelta


class IBKRClient:
    """Thin wrapper around ib_insync for historical OHLC data."""

    def __init__(self, host: str, port: int, client_id: int, market_data_type: int = 1):
        self.ib = IB()
        # You must have TWS or IB Gateway running locally.
        self.ib.connect(host, port, clientId=client_id)
        # 1 = live, 2 = frozen, 3 = delayed, 4 = delayed-frozen
        self.ib.reqMarketDataType(market_data_type)

    def get_historical_ohlc(self, symbol: str, bar_size: str, lookback_days: int) -> pd.DataFrame:
        contract = Stock(symbol, "SMART", "USD")
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=f"{lookback_days} D",
            barSizeSetting=bar_size,
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1
        )
        df = util.df(bars)
        # Normalize column names
        df.rename(columns={
            "date": "time",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume"
        }, inplace=True)
        df.set_index("time", inplace=True)
        return df


class MockIBKRClient:
    """Mock client to generate deterministic OHLC data for CI/offline runs."""

    def __init__(self, seed: int = 42):
        self._rng = _np.random.default_rng(seed)

    def get_historical_ohlc(self, symbol: str, bar_size: str, lookback_days: int) -> _pd.DataFrame:
        # Only supports daily bars in mock; ignore bar_size variations.
        end = datetime.utcnow().date()
        dates = [end - timedelta(days=i) for i in range(lookback_days)]
        dates.reverse()

        base = 100.0 + abs(hash(symbol)) % 50
        noise = self._rng.normal(0, 1, size=len(dates))

        closes = base + _np.cumsum(noise)
        opens = closes + self._rng.normal(0, 0.5, size=len(dates))
        highs = _np.maximum(opens, closes) + abs(self._rng.normal(0, 0.7, size=len(dates)))
        lows = _np.minimum(opens, closes) - abs(self._rng.normal(0, 0.7, size=len(dates)))
        volumes = self._rng.integers(1_000_000, 5_000_000, size=len(dates))

        df = _pd.DataFrame({
            "time": [datetime.combine(d, datetime.min.time()) for d in dates],
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        })
        df.set_index("time", inplace=True)
        return df
