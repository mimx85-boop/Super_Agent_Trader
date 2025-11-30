# Super Agent Trader

An automated trading agent that fetches market data, trains machine learning models, and generates trading predictions.

## Architecture

### Pipeline Overview

The system runs a 3-step daily workflow:

1. **DataAgent** - Fetches OHLC data from IBKR for configured symbols (AAPL, MSFT, TSLA) and stores as parquet files in S3
2. **MLAgent** - Trains LightGBM models on the latest market data with engineered features
3. **PredictAgent** - Generates probability predictions for upward movement and saves results to S3

### Components

- **Agents** (`agents/`):
  - `super_agent.py` - Orchestrates the 3-step pipeline
  - `data_agent.py` - IBKR market data collection
  - `ml_agent.py` - Model training (LightGBM)
  - `predict_agent.py` - Prediction generation
  - `base_agent.py` - Base class with shared functionality

- **Utilities** (`utils/`):
  - `ibkr_client.py` - IBKR API wrapper using ib_insync
  - `s3_client.py` - S3 parquet I/O operations
  - `features.py` - Feature engineering for ML models

### Configuration

Edit `config.yaml` to customize:
- IBKR connection (host, port, client_id)
- AWS S3 bucket and region
- Trading symbols and data parameters
- Training and prediction settings

## Setup

### Prerequisites

- Python 3.11+
- IBKR TWS/Gateway running on localhost:7496
- AWS credentials configured (`~/.aws/credentials`)

### Installation

1. Clone the repository
2. Create and activate the virtual environment:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
   .\setup_venv.ps1
   ```

3. Verify the environment:
   ```powershell
   .\venv\Scripts\python --version
   ```

## Usage

### Run the daily pipeline

```powershell
.\venv\Scripts\python main.py
```

Expected output:
```
Step 1: Updating data from IBKR → S3
  Writing raw data for AAPL to s3://bucket/raw/AAPL/...
  Writing raw data for MSFT to s3://bucket/raw/MSFT/...
  Writing raw data for TSLA to s3://bucket/raw/TSLA/...

Step 2: Training / updating models
  Training LightGBM model for AAPL
  Training LightGBM model for MSFT
  Training LightGBM model for TSLA

Step 3: Running predictions
  AAPL: P(up)=0.600 at 2025-11-28
  MSFT: P(up)=0.400 at 2025-11-28
  TSLA: P(up)=0.600 at 2025-11-28

Final prediction snapshot: {'AAPL': 0.6, 'MSFT': 0.4, 'TSLA': 0.6}
```

### Development Tools

- **Format code**: `.\venv\Scripts\black agents/ utils/`
- **Lint code**: `.\venv\Scripts\flake8 agents/ utils/`
- **Run tests**: `.\venv\Scripts\pytest tests/`

## Dependencies

- `ib-insync` - IBKR API client
- `boto3` - AWS S3 interaction
- `pandas` - Data manipulation
- `pyarrow` - Parquet file support
- `lightgbm` - Gradient boosting models
- `pyyaml` - YAML configuration parsing
- `black` - Code formatting
- `pytest` - Testing framework
- `flake8` - Code linting

## File Structure

```
Super_Agent_Trader/
├── agents/                 # Agent classes
│   ├── __init__.py
│   ├── base_agent.py
│   ├── data_agent.py
│   ├── ml_agent.py
│   ├── predict_agent.py
│   └── super_agent.py
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── ibkr_client.py
│   ├── s3_client.py
│   └── features.py
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_agents.py
│   └── test_s3_client.py
├── config.yaml            # Configuration
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Development config (black, pytest, flake8)
├── .gitignore             # Git ignore rules
├── .vscode/settings.json  # VS Code configuration
├── README.md              # This file
└── setup_venv.ps1         # Virtual environment setup script
```

## Environment Variables

Ensure AWS credentials are configured:
```bash
# ~/.aws/credentials
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

## Logs

Logs are printed to console with timestamps and log levels. Each component logs its operations:
- IBKR connections and API events
- Data fetch and S3 write operations
- Model training progress
- Prediction generation

## Troubleshooting

### "ModuleNotFoundError: No module named 'ib_insync'"
Ensure the virtual environment is activated and packages are installed:
```powershell
.\venv\Scripts\pip install -r requirements.txt
```

### "io.UnsupportedOperation: seek"
This has been fixed in the current version. Parquet files are properly read into BytesIO objects.

### "LightGBMError: Model file ... is not available for writes"
Fixed in current version. Models are saved via temporary files.

## Next Steps

- Implement proper unit tests with S3 mocking
- Add backtesting functionality
- Deploy as scheduled Lambda or CloudWatch event
- Add real-time WebSocket data feeds
- Implement risk management and position sizing

## License

Internal use only.
