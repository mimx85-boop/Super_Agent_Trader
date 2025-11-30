from datetime import datetime
from io import BytesIO
import tempfile
import os
from .base_agent import BaseAgent
from utils.s3_client import S3Client
from utils.features import add_features
import pandas as pd
import lightgbm as lgb


class PredictAgent(BaseAgent):
    """Loads model + latest data from S3, generates predictions and writes them back to S3."""

    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(config_path)
        aws_cfg = self.config["aws"]
        self.s3 = S3Client(
            region=aws_cfg["region"],
            bucket=aws_cfg["s3_bucket"]
        )

    def _load_model(self, symbol: str) -> lgb.Booster:
        model_prefix = self.config["paths"]["model_prefix"]
        model_key = f"{model_prefix}{symbol}/model.txt"
        obj = self.s3.s3.get_object(Bucket=self.s3.bucket, Key=model_key)
        
        # Save model to temp file, then load
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as tmp:
            tmp.write(obj["Body"].read())
            tmp_path = tmp.name
        
        try:
            model = lgb.Booster(model_file=tmp_path)
            return model
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def predict_symbol(self, symbol: str):
        raw_prefix = self.config["paths"]["raw_prefix"]
        prefix = f"{raw_prefix}{symbol}/"
        latest_key = self.s3.get_latest_key(prefix)
        if latest_key is None:
            self.logger.warning(f"No raw data found for {symbol}; cannot predict.")
            return None

        self.logger.info(f"Predicting with latest raw data: {latest_key}")
        df = self.s3.read_parquet(latest_key)

        df_feat = add_features(df)
        if df_feat.empty:
            self.logger.warning(f"No features for {symbol}; cannot predict.")
            return None

        X = df_feat.drop(columns=["target_up"])

        model = self._load_model(symbol)
        preds = model.predict(X)

        latest_prob = float(preds[-1])
        latest_time = df_feat.index[-1]
        self.logger.info(f"{symbol}: P(up)={latest_prob:.3f} at {latest_time}")

        # Save full prediction series
        pred_prefix = self.config["paths"]["pred_prefix"]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
        pred_key = f"{pred_prefix}{symbol}/{timestamp}.parquet"
        out_df = pd.DataFrame({
            "time": df_feat.index,
            "p_up": preds,
        })
        out_df.set_index("time", inplace=True)
        self.s3.write_parquet(out_df, pred_key)
        self.logger.info(f"Wrote predictions to s3://{self.s3.bucket}/{pred_key}")

        return latest_prob

    def run(self):
        results = {}
        for symbol in self.config["symbols"]:
            prob = self.predict_symbol(symbol)
            results[symbol] = prob
        return results
