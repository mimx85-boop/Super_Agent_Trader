#!/usr/bin/env python3
"""Create config.yaml from environment variables."""
import os
import yaml

config = {
    'ibkr': {
        'host': os.getenv('IBKR_HOST', '127.0.0.1'),
        'port': int(os.getenv('IBKR_PORT', '7496')),
        'client_id': 1,
        'market_data_type': 3
    },
    'aws': {
        'region': os.getenv('AWS_REGION', 'us-east-1'),
        's3_bucket': os.getenv('S3_BUCKET', 'stock-trade-data-2025')
    },
    'symbols': ['AAPL', 'MSFT', 'TSLA'],
    'data': {
        'bar_size': '1 day',
        'lookback_days': 30
    },
    'training': {
        'retrain_days': 1,
        'model_type': 'lightgbm',
        'target': 'direction'
    },
    'paths': {
        'raw_prefix': 'raw/',
        'feature_prefix': 'features/',
        'model_prefix': 'model/',
        'pred_prefix': 'predictions/'
    }
}

with open('config.yaml', 'w') as f:
    yaml.dump(config, f)

print("✓ config.yaml created successfully")
