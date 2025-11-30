"""Analytics queries for Redshift data analysis."""
import boto3
import pandas as pd
from utils.s3_client import S3Client
import yaml
from datetime import datetime


class RedshiftAnalytics:
    """Advanced analytics for trading data."""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        aws_cfg = self.config["aws"]
        self.s3_client = S3Client(region=aws_cfg["region"], bucket=aws_cfg["s3_bucket"])
        self.s3_bucket = aws_cfg["s3_bucket"]
        self.region = aws_cfg["region"]

    def analyze_symbol(self, symbol: str) -> dict:
        """Comprehensive analysis of a symbol."""
        prefix = f"raw/{symbol}/"
        latest_key = self.s3_client.get_latest_key(prefix)
        
        if not latest_key:
            return {"error": f"No data found for {symbol}"}
        
        df = self.s3_client.read_parquet(latest_key)
        
        # Calculate metrics
        returns = df['close'].pct_change()
        price_range = df['high'] - df['low']
        
        # Handle date formatting (index might already be date or datetime)
        first_date = df.index[0]
        last_date = df.index[-1]
        if hasattr(first_date, 'date'):
            first_date = first_date.date()
        if hasattr(last_date, 'date'):
            last_date = last_date.date()
        
        analysis = {
            "symbol": symbol,
            "file": latest_key,
            "data_points": len(df),
            "date_range": f"{first_date} to {last_date}",
            
            # Price metrics
            "current_price": float(df['close'].iloc[-1]),
            "price_min": float(df['close'].min()),
            "price_max": float(df['close'].max()),
            "price_avg": float(df['close'].mean()),
            
            # Returns
            "total_return": float((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100),
            "daily_return_avg": float(returns.mean() * 100),
            "daily_return_std": float(returns.std() * 100),
            "max_daily_gain": float(returns.max() * 100),
            "max_daily_loss": float(returns.min() * 100),
            
            # Volatility
            "volatility": float(returns.std() * 100),
            "avg_price_range": float(price_range.mean()),
            "max_intraday_range": float(price_range.max()),
            
            # Volume
            "avg_volume": float(df['volume'].mean()),
            "total_volume": float(df['volume'].sum()),
            
            # Trend
            "updays": int((returns > 0).sum()),
            "downdays": int((returns < 0).sum()),
            "win_rate": float((returns > 0).sum() / len(returns) * 100),
        }
        
        return analysis

    def compare_symbols(self, symbols: list) -> pd.DataFrame:
        """Compare multiple symbols side by side."""
        results = []
        for symbol in symbols:
            analysis = self.analyze_symbol(symbol)
            results.append(analysis)
        
        df = pd.DataFrame(results)
        return df[["symbol", "current_price", "total_return", "volatility", 
                   "daily_return_avg", "avg_volume", "win_rate"]]

    def correlation_analysis(self, symbols: list) -> dict:
        """Analyze correlations between symbols."""
        price_data = {}
        
        for symbol in symbols:
            prefix = f"raw/{symbol}/"
            latest_key = self.s3_client.get_latest_key(prefix)
            if latest_key:
                df = self.s3_client.read_parquet(latest_key)
                price_data[symbol] = df['close']
        
        if not price_data:
            return {"error": "No data available"}
        
        prices_df = pd.DataFrame(price_data)
        correlations = prices_df.corr().to_dict()
        
        return {
            "correlations": correlations,
            "data_shape": prices_df.shape,
        }

    def volatility_comparison(self, symbols: list) -> dict:
        """Compare volatility metrics."""
        volatility_data = {}
        
        for symbol in symbols:
            prefix = f"raw/{symbol}/"
            latest_key = self.s3_client.get_latest_key(prefix)
            
            if latest_key:
                df = self.s3_client.read_parquet(latest_key)
                returns = df['close'].pct_change()
                
                volatility_data[symbol] = {
                    "daily_volatility": float(returns.std() * 100),
                    "annualized_volatility": float(returns.std() * (252 ** 0.5) * 100),
                    "sharpe_ratio": float((returns.mean() / returns.std() * (252 ** 0.5)) if returns.std() > 0 else 0),
                    "max_drawdown": float((df['close'].min() - df['close'].max()) / df['close'].max() * 100),
                }
        
        return volatility_data

    def performance_summary(self, symbols: list) -> dict:
        """Generate overall performance summary."""
        summary = {}
        
        for symbol in symbols:
            analysis = self.analyze_symbol(symbol)
            summary[symbol] = {
                "price": analysis.get("current_price"),
                "return": analysis.get("total_return"),
                "volatility": analysis.get("volatility"),
                "sharpe_approx": analysis.get("daily_return_avg", 0) / analysis.get("daily_return_std", 1) if analysis.get("daily_return_std", 1) > 0 else 0,
                "win_rate": analysis.get("win_rate"),
            }
        
        return summary


if __name__ == "__main__":
    analytics = RedshiftAnalytics("config.yaml")
    symbols = ["AAPL", "MSFT", "TSLA"]
    
    print("\n" + "=" * 80)
    print("SYMBOL ANALYSIS")
    print("=" * 80)
    for symbol in symbols:
        analysis = analytics.analyze_symbol(symbol)
        print(f"\n{symbol}:")
        for key, value in analysis.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("COMPARISON")
    print("=" * 80)
    comparison = analytics.compare_symbols(symbols)
    print(comparison.to_string())
    
    print("\n" + "=" * 80)
    print("CORRELATION ANALYSIS")
    print("=" * 80)
    corr = analytics.correlation_analysis(symbols)
    print(corr)
    
    print("\n" + "=" * 80)
    print("VOLATILITY COMPARISON")
    print("=" * 80)
    vol = analytics.volatility_comparison(symbols)
    for symbol, metrics in vol.items():
        print(f"\n{symbol}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.2f}")
