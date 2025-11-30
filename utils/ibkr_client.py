from ib_insync import IB, Stock, util
import pandas as pd


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
