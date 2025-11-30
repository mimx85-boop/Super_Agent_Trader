from io import BytesIO
import tempfile
import os
from .base_agent import BaseAgent
from utils.s3_client import S3Client
from utils.features import add_features
import lightgbm as lgb


class MLAgent(BaseAgent):
    """Loads raw data from S3, builds features, trains a LightGBM model, saves to S3."""

    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(config_path)
        aws_cfg = self.config["aws"]
        self.s3 = S3Client(
            region=aws_cfg["region"],
            bucket=aws_cfg["s3_bucket"]
        )

    def train_symbol(self, symbol: str):
        raw_prefix = self.config["paths"]["raw_prefix"]
        prefix = f"{raw_prefix}{symbol}/"
        latest_key = self.s3.get_latest_key(prefix)
        if latest_key is None:
            self.logger.warning(f"No raw data found for {symbol} under prefix {prefix}")
            return

        self.logger.info(f"Training on latest raw data: {latest_key}")
        df = self.s3.read_parquet(latest_key)

        df_feat = add_features(df)
        if df_feat.empty:
            self.logger.warning(f"No features available for {symbol}; skipping.")
            return

        X = df_feat.drop(columns=["target_up"])
        y = df_feat["target_up"]

        train_dataset = lgb.Dataset(X, label=y)
        params = {
            "objective": "binary",
            "metric": "binary_logloss",
            "learning_rate": 0.02,
            "num_leaves": 32,
            "feature_fraction": 0.8,
            "verbose": -1,
        }

        self.logger.info(f"Training LightGBM model for {symbol}")
        model = lgb.train(params, train_dataset, num_boost_round=200)

        model_prefix = self.config["paths"]["model_prefix"]
        model_key = f"{model_prefix}{symbol}/model.txt"
        
        # Save model to temp file, then read and upload to S3
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp_path = tmp.name
        
        try:
            model.save_model(tmp_path)
            with open(tmp_path, 'rb') as f:
                self.s3.s3.put_object(
                    Bucket=self.s3.bucket,
                    Key=model_key,
                    Body=f.read()
                )
            self.logger.info(f"Saved model for {symbol} to s3://{self.s3.bucket}/{model_key}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def run(self):
        for symbol in self.config["symbols"]:
            self.train_symbol(symbol)
