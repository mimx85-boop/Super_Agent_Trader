from datetime import datetime
import os
from .base_agent import BaseAgent
from utils.ibkr_client import IBKRClient, MockIBKRClient
from utils.s3_client import S3Client


class DataAgent(BaseAgent):
    """Fetches historical OHLC from IBKR and writes to S3."""

    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(config_path)
        ib_cfg = self.config["ibkr"]
        aws_cfg = self.config["aws"]

        use_mock = os.environ.get("OFFLINE_MODE") == "true" or os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
        if use_mock:
            self.logger.warning("CI/OFFLINE mode detected — using MockIBKRClient for data.")
            self.ib = MockIBKRClient()
        else:
            # Allow env overrides for host/port if provided
            host = os.environ.get("IBKR_HOST", ib_cfg["host"])
            port = int(os.environ.get("IBKR_PORT", ib_cfg["port"]))
            try:
                self.ib = IBKRClient(
                    host=host,
                    port=port,
                    client_id=ib_cfg["client_id"],
                    market_data_type=ib_cfg.get("market_data_type", 1)
                )
            except Exception as e:
                self.logger.error(f"IBKR connection failed ({host}:{port}). Falling back to mock client. Error: {e}")
                self.ib = MockIBKRClient()

        self.s3 = S3Client(
            region=aws_cfg["region"],
            bucket=aws_cfg["s3_bucket"]
        )

    def update_symbol(self, symbol: str):
        bar_size = self.config["data"]["bar_size"]
        lookback = self.config["data"]["lookback_days"]
        df = self.ib.get_historical_ohlc(symbol, bar_size, lookback)

        date_str = datetime.utcnow().strftime("%Y%m%d_%H%M")
        key = f"{self.config['paths']['raw_prefix']}{symbol}/{date_str}.parquet"
        self.logger.info(f"Writing raw data for {symbol} to s3://{self.s3.bucket}/{key}")
        self.s3.write_parquet(df, key)

    def run(self):
        for symbol in self.config["symbols"]:
            self.update_symbol(symbol)
