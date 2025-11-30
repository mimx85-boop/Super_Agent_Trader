"""Redshift client for querying S3 data."""
import boto3
import pandas as pd
from typing import Optional
import yaml


class RedshiftClient:
    """Connect to Redshift and query S3 data stored as parquet files."""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        aws_cfg = self.config["aws"]
        self.redshift = boto3.client("redshift-data", region_name=aws_cfg["region"])
        self.s3_bucket = aws_cfg["s3_bucket"]
        self.region = aws_cfg["region"]

    def query_raw_data(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """
        Query raw OHLC data for a symbol from S3.
        Uses Redshift Spectrum to query parquet files directly.
        """
        # Construct S3 path
        s3_path = f"s3://{self.s3_bucket}/raw/{symbol}/"
        
        # SQL query using Redshift Spectrum (queries S3 directly)
        query = f"""
        SELECT *
        FROM s3object
        WHERE '$path' LIKE '{s3_path}%.parquet'
        LIMIT {limit}
        """
        
        print(f"Querying S3 path: {s3_path}")
        print(f"Query: {query}")
        
        # For now, just return the path info
        # In production, you'd execute this against Redshift
        return {"status": "ready", "s3_path": s3_path, "query": query}

    def list_s3_files(self, prefix: str) -> list:
        """List all files in S3 with given prefix."""
        s3 = boto3.client("s3", region_name=self.region)
        keys = []
        continuation_token = None
        
        while True:
            kwargs = {"Bucket": self.s3_bucket, "Prefix": prefix}
            if continuation_token:
                kwargs["ContinuationToken"] = continuation_token
            
            resp = s3.list_objects_v2(**kwargs)
            for item in resp.get("Contents", []):
                keys.append(item["Key"])
            
            if resp.get("IsTruncated"):
                continuation_token = resp.get("NextContinuationToken")
            else:
                break
        
        return keys

    def get_symbol_stats(self, symbol: str) -> dict:
        """Get statistics about a symbol's data in S3."""
        prefix = f"raw/{symbol}/"
        files = self.list_s3_files(prefix)
        
        return {
            "symbol": symbol,
            "file_count": len(files),
            "latest_file": files[-1] if files else None,
            "all_files": files
        }


if __name__ == "__main__":
    # Example usage
    redshift = RedshiftClient("config.yaml")
    
    # List stats for each symbol
    for symbol in ["AAPL", "MSFT", "TSLA"]:
        stats = redshift.get_symbol_stats(symbol)
        print(f"\n{symbol} Stats:")
        print(f"  Files: {stats['file_count']}")
        print(f"  Latest: {stats['latest_file']}")
