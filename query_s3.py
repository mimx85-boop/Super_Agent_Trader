#!/usr/bin/env python3
"""Simple script to query and display S3 data."""
import sys
from utils.s3_client import S3Client
from utils.redshift_client import RedshiftClient
import yaml


def show_s3_contents():
    """Display what's in your S3 bucket."""
    
    # Load config
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    
    aws_cfg = config["aws"]
    s3_client = S3Client(region=aws_cfg["region"], bucket=aws_cfg["s3_bucket"])
    
    print("=" * 80)
    print("S3 BUCKET CONTENTS")
    print("=" * 80)
    
    # Show raw data
    print("\n📊 RAW DATA (OHLC from IBKR):")
    print("-" * 80)
    raw_keys = s3_client.list_keys("raw/")
    for key in raw_keys:
        print(f"  ✓ {key}")
    
    # Show models
    print("\n🤖 TRAINED MODELS:")
    print("-" * 80)
    model_keys = s3_client.list_keys("model/")
    for key in model_keys:
        print(f"  ✓ {key}")
    
    # Show predictions
    print("\n🎯 PREDICTIONS:")
    print("-" * 80)
    pred_keys = s3_client.list_keys("predictions/")
    for key in pred_keys:
        print(f"  ✓ {key}")
    
    # Show features
    print("\n🔧 FEATURES:")
    print("-" * 80)
    feat_keys = s3_client.list_keys("features/")
    if feat_keys:
        for key in feat_keys:
            print(f"  ✓ {key}")
    else:
        print("  (no feature files yet)")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"  Raw files: {len(raw_keys)}")
    print(f"  Models: {len(model_keys)}")
    print(f"  Predictions: {len(pred_keys)}")
    print(f"  Features: {len(feat_keys)}")
    print("=" * 80)


def show_redshift_stats():
    """Show stats about data using Redshift."""
    
    print("\n📈 DATA STATISTICS (via Redshift):")
    print("-" * 80)
    
    redshift = RedshiftClient("config.yaml")
    
    for symbol in ["AAPL", "MSFT", "TSLA"]:
        stats = redshift.get_symbol_stats(symbol)
        print(f"\n{symbol}:")
        print(f"  Files stored: {stats['file_count']}")
        if stats['latest_file']:
            print(f"  Latest file: {stats['latest_file']}")


def read_latest_data(symbol: str):
    """Read and display the latest data for a symbol."""
    
    print(f"\n📥 READING LATEST DATA FOR {symbol}:")
    print("-" * 80)
    
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    
    aws_cfg = config["aws"]
    s3_client = S3Client(region=aws_cfg["region"], bucket=aws_cfg["s3_bucket"])
    
    prefix = f"raw/{symbol}/"
    latest_key = s3_client.get_latest_key(prefix)
    
    if latest_key:
        print(f"Reading: {latest_key}")
        df = s3_client.read_parquet(latest_key)
        print(f"\nShape: {df.shape}")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst few rows:")
        print(df.head())
    else:
        print(f"No data found for {symbol}")


if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "read":
            symbol = sys.argv[2].upper() if len(sys.argv) > 2 else "AAPL"
            read_latest_data(symbol)
        else:
            print("Usage: python query_s3.py [read SYMBOL]")
    else:
        # Default: show S3 contents and stats
        show_s3_contents()
        show_redshift_stats()
