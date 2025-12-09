from datetime import datetime
import os
from .base_agent import BaseAgent
from utils.ibkr_client import IBKRClient, MockIBKRClient
from utils.s3_client import S3Client
from pathlib import Path
import csv


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
        # Delete oldest file in symbol folder to keep storage tidy
        deleted = self.s3.delete_oldest(f"{self.config['paths']['raw_prefix']}{symbol}/")
        if deleted:
            self.logger.info(f"Deleted oldest file for {symbol}: s3://{self.s3.bucket}/{deleted}")

    def run(self):
        symbols = self._resolve_symbols()
        self.logger.info(f"Symbols to update: {symbols}")
        for symbol in symbols:
            self.update_symbol(symbol)

    def _resolve_symbols(self):
        # Support dynamic symbol resolution
        cfg_syms = self.config.get("symbols")
        if isinstance(cfg_syms, list) and cfg_syms:
            return cfg_syms
        if isinstance(cfg_syms, str) and cfg_syms.strip() == "*":
            # Priority 1: local CSV at data/tickers.csv
            csv_path = Path("data") / "tickers.csv"
            if csv_path.exists():
                syms = []
                with csv_path.open("r", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        val = row.get("symbol") or row.get("ticker")
                        if val:
                            syms.append(val.strip())
                if syms:
                    return syms
            # Priority 2: latest analytics_symbols_*.csv
            logs_dir = Path("logs")
            candidates = sorted(logs_dir.glob("analytics_symbols_*.csv"))
            if candidates:
                latest = candidates[-1]
                syms = []
                with latest.open("r", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "symbol" in row and row["symbol"]:
                            syms.append(row["symbol"].strip())
                if syms:
                    return syms
            # Priority 3: discover prefixes in S3 under raw/
            raw_prefix = self.config["paths"]["raw_prefix"]
            prefixes = self.s3.list_prefixes(raw_prefix)
            syms = [p.replace(raw_prefix, "").strip("/") for p in prefixes]
            if syms:
                return syms
        # Final fallback: empty list
        self.logger.warning("No symbols found. Ensure config.yaml symbols list or set symbols: '*'.")
        return []
