"""Generate lightweight Plotly visualizations for trading data."""
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
from s3_client import S3Client


class TradingDashboard:
    """Create interactive Plotly dashboards and store in S3."""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.s3_client = S3Client(
            region=self.config["aws"]["region"],
            bucket=self.config["aws"]["s3_bucket"]
        )
        self.symbols = self.config.get("symbols", [])
        self.viz_dir = Path("visualizations")
        self.viz_dir.mkdir(exist_ok=True)

    def create_price_chart(self, symbol: str, days: int = 30) -> Path:
        """Create candlestick + volume chart."""
        # Get latest parquet file
        s3_path = f"raw/{symbol}"
        latest_file = self.s3_client.get_latest_key(s3_path)
        
        if not latest_file:
            print(f"No data found for {symbol}")
            return None
        
        df = self.s3_client.read_parquet(latest_file)
        df = df.tail(days)
        
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Add candlestick
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=symbol,
                increasing_line_color='#00CC96',
                decreasing_line_color='#FF6D6D'
            ),
            row=1, col=1
        )
        
        # Add volume bars
        colors = ['#00CC96' if close >= open_ else '#FF6D6D' 
                  for close, open_ in zip(df['close'], df['open'])]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.6,
                showlegend=False
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        fig.update_layout(
            title=f"{symbol} - Price & Volume (Last {days} Days)",
            hovermode='x unified',
            height=600,
            template='plotly_dark',
            font=dict(size=11)
        )
        
        # Save locally
        html_file = self.viz_dir / f"{symbol}_price_chart.html"
        fig.write_html(html_file)
        
        return html_file

    def create_comparison_chart(self) -> Path:
        """Compare returns across all symbols."""
        data = []
        
        for symbol in self.symbols:
            latest_file = self.s3_client.get_latest_key(f"raw/{symbol}")
            if latest_file:
                df = self.s3_client.read_parquet(latest_file)
                total_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
                data.append({"symbol": symbol, "return": total_return})
        
        df_returns = pd.DataFrame(data)
        
        fig = go.Figure()
        
        colors = ['#00CC96' if x >= 0 else '#FF6D6D' for x in df_returns['return']]
        
        fig.add_trace(
            go.Bar(
                x=df_returns['symbol'],
                y=df_returns['return'],
                marker_color=colors,
                text=[f"{x:.2f}%" for x in df_returns['return']],
                textposition='outside',
                name='Total Return'
            )
        )
        
        fig.update_layout(
            title="Total Return Comparison (30-Day Period)",
            xaxis_title="Symbol",
            yaxis_title="Return (%)",
            hovermode='x',
            height=500,
            template='plotly_dark',
            font=dict(size=12),
            showlegend=False
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        html_file = self.viz_dir / "comparison_returns.html"
        fig.write_html(html_file)
        
        return html_file

    def create_volatility_chart(self) -> Path:
        """Volatility comparison chart."""
        data = []
        
        for symbol in self.symbols:
            latest_file = self.s3_client.get_latest_key(f"raw/{symbol}")
            if latest_file:
                df = self.s3_client.read_parquet(latest_file)
                daily_vol = df['close'].pct_change().std() * 100
                data.append({"symbol": symbol, "volatility": daily_vol})
        
        df_vol = pd.DataFrame(data).sort_values('volatility', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=df_vol['symbol'],
                y=df_vol['volatility'],
                marker_color=['#FF6D6D' if x > 2 else '#FFA500' if x > 1.5 else '#00CC96' 
                              for x in df_vol['volatility']],
                text=[f"{x:.2f}%" for x in df_vol['volatility']],
                textposition='outside',
                name='Daily Volatility'
            )
        )
        
        fig.update_layout(
            title="Daily Volatility Comparison",
            xaxis_title="Symbol",
            yaxis_title="Daily Volatility (%)",
            hovermode='x',
            height=500,
            template='plotly_dark',
            font=dict(size=12),
            showlegend=False
        )
        
        html_file = self.viz_dir / "volatility_comparison.html"
        fig.write_html(html_file)
        
        return html_file

    def create_correlation_heatmap(self) -> Path:
        """Create correlation matrix heatmap."""
        data_frames = {}
        
        for symbol in self.symbols:
            latest_file = self.s3_client.get_latest_key(f"raw/{symbol}")
            if latest_file:
                df = self.s3_client.read_parquet(latest_file)
                data_frames[symbol] = df['close'].pct_change()
        
        corr_df = pd.DataFrame(data_frames).corr()
        
        fig = go.Figure(
            data=go.Heatmap(
                z=corr_df.values,
                x=corr_df.columns,
                y=corr_df.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_df.values,
                texttemplate='%{text:.3f}',
                textfont={"size": 14},
                colorbar=dict(title="Correlation")
            )
        )
        
        fig.update_layout(
            title="Price Correlation Matrix",
            height=500,
            width=600,
            template='plotly_dark'
        )
        
        html_file = self.viz_dir / "correlation_heatmap.html"
        fig.write_html(html_file)
        
        return html_file

    def create_master_dashboard(self) -> Path:
        """Create main HTML dashboard linking all charts."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Super Agent Trader - Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            background: rgba(0, 0, 0, 0.3);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #00CC96;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #00CC96;
        }}
        header p {{
            color: #a0a0a0;
            font-size: 0.95em;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        .chart-card {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(0, 204, 150, 0.2);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }}
        .chart-card:hover {{
            border-color: rgba(0, 204, 150, 0.5);
            box-shadow: 0 6px 12px rgba(0, 204, 150, 0.2);
        }}
        .chart-card h3 {{
            color: #00CC96;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        iframe {{
            width: 100%;
            height: 500px;
            border: none;
            border-radius: 5px;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #707070;
            font-size: 0.9em;
            border-top: 1px solid rgba(0, 204, 150, 0.1);
            margin-top: 30px;
        }}
        a {{
            color: #00CC96;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>SUPER AGENT TRADER - DASHBOARD</h1>
            <p>Last Updated: {timestamp}</p>
            <p>Real-time analytics powered by your trading data in S3</p>
        </header>
        
        <div class="dashboard-grid">
            <div class="chart-card full-width">
                <h3>Returns Comparison</h3>
                <iframe src="comparison_returns.html" title="Returns Comparison"></iframe>
            </div>
            
            <div class="chart-card">
                <h3>AAPL - Price & Volume</h3>
                <iframe src="AAPL_price_chart.html" title="AAPL Chart"></iframe>
            </div>
            
            <div class="chart-card">
                <h3>MSFT - Price & Volume</h3>
                <iframe src="MSFT_price_chart.html" title="MSFT Chart"></iframe>
            </div>
            
            <div class="chart-card">
                <h3>TSLA - Price & Volume</h3>
                <iframe src="TSLA_price_chart.html" title="TSLA Chart"></iframe>
            </div>
            
            <div class="chart-card">
                <h3>Volatility Comparison</h3>
                <iframe src="volatility_comparison.html" title="Volatility"></iframe>
            </div>
            
            <div class="chart-card">
                <h3>Price Correlation Matrix</h3>
                <iframe src="correlation_heatmap.html" title="Correlation"></iframe>
            </div>
        </div>
        
        <footer>
            <p>For detailed analytics reports, see logs/analytics_data_*.json</p>
            <p>Dashboard generated automatically by AnalyticsReporter</p>
        </footer>
    </div>
</body>
</html>
"""
        
        html_file = self.viz_dir / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file

    def generate_all_visualizations(self) -> dict:
        """Generate all charts and return file locations."""
        print("Generating visualizations...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }
        
        # Individual price charts
        for symbol in self.symbols:
            try:
                chart_file = self.create_price_chart(symbol)
                results["files"][f"{symbol}_price"] = str(chart_file)
                print(f"  ✓ {symbol} price chart")
            except Exception as e:
                print(f"  ✗ {symbol} price chart: {e}")
        
        # Comparison chart
        try:
            comp_file = self.create_comparison_chart()
            results["files"]["comparison"] = str(comp_file)
            print(f"  ✓ Comparison chart")
        except Exception as e:
            print(f"  ✗ Comparison chart: {e}")
        
        # Volatility chart
        try:
            vol_file = self.create_volatility_chart()
            results["files"]["volatility"] = str(vol_file)
            print(f"  ✓ Volatility chart")
        except Exception as e:
            print(f"  ✗ Volatility chart: {e}")
        
        # Correlation heatmap
        try:
            corr_file = self.create_correlation_heatmap()
            results["files"]["correlation"] = str(corr_file)
            print(f"  ✓ Correlation heatmap")
        except Exception as e:
            print(f"  ✗ Correlation heatmap: {e}")
        
        # Master dashboard
        try:
            dashboard_file = self.create_master_dashboard()
            results["files"]["dashboard"] = str(dashboard_file)
            print(f"  ✓ Master dashboard (index.html)")
        except Exception as e:
            print(f"  ✗ Master dashboard: {e}")
        
        return results


if __name__ == "__main__":
    dashboard = TradingDashboard()
    results = dashboard.generate_all_visualizations()
    
    print("\n" + "=" * 60)
    print("Visualizations created in: visualizations/")
    print("Open 'visualizations/index.html' in your browser")
    print("=" * 60)
    
    print("\nFile listing:")
    for name, path in results["files"].items():
        print(f"  {name}: {path}")
