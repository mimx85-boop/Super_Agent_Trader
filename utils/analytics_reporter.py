"""Analytics reporting module with extensible logging."""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
try:
    from utils.redshift_analytics import RedshiftAnalytics
except ImportError:
    from .redshift_analytics import RedshiftAnalytics
import yaml


class AnalyticsReporter:
    """Generate structured analytics reports with extensible logging."""

    def __init__(self, config_path: str = "config.yaml", log_dir: str = "logs"):
        self.config_path = config_path
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.symbols = self.config.get("symbols", [])
        self.analytics = RedshiftAnalytics(config_path)
        
        # Setup logger
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup structured logger."""
        logger = logging.getLogger("AnalyticsReporter")
        logger.setLevel(logging.DEBUG)
        
        # File handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"analytics_report_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def generate_full_report(self) -> dict:
        """Generate comprehensive analytics report."""
        self.logger.info("=" * 80)
        self.logger.info("STARTING COMPREHENSIVE ANALYTICS REPORT")
        self.logger.info("=" * 80)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "symbols": self.symbols,
            "symbol_analysis": {},
            "comparison": {},
            "correlations": {},
            "volatility": {},
            "performance_summary": {},
        }
        
        # Symbol-level analysis
        self.logger.info("\n[1/5] Analyzing individual symbols...")
        for symbol in self.symbols:
            self.logger.debug(f"  Analyzing {symbol}...")
            analysis = self.analytics.analyze_symbol(symbol)
            report["symbol_analysis"][symbol] = analysis
            self.logger.info(f"  ✓ {symbol}: Price=${analysis.get('current_price', 'N/A'):.2f}, Return={analysis.get('total_return', 0):.2f}%")
        
        # Comparison
        self.logger.info("\n[2/5] Running comparison analysis...")
        try:
            comparison_df = self.analytics.compare_symbols(self.symbols)
            report["comparison"] = comparison_df.to_dict(orient="records")
            self.logger.info(f"  ✓ Compared {len(self.symbols)} symbols")
        except Exception as e:
            self.logger.error(f"  ✗ Comparison failed: {e}")
        
        # Correlations
        self.logger.info("\n[3/5] Calculating correlations...")
        try:
            corr = self.analytics.correlation_analysis(self.symbols)
            report["correlations"] = corr
            self.logger.info(f"  ✓ Correlation matrix calculated")
            # Log correlation pairs
            if "correlations" in corr:
                for sym1, corrs in corr["correlations"].items():
                    for sym2, value in corrs.items():
                        if sym1 < sym2:  # Avoid duplicates
                            self.logger.debug(f"    {sym1}-{sym2}: {value:.3f}")
        except Exception as e:
            self.logger.error(f"  ✗ Correlation analysis failed: {e}")
        
        # Volatility
        self.logger.info("\n[4/5] Analyzing volatility...")
        try:
            vol = self.analytics.volatility_comparison(self.symbols)
            report["volatility"] = vol
            for symbol, metrics in vol.items():
                self.logger.info(f"  {symbol}:")
                self.logger.info(f"    Daily Volatility: {metrics['daily_volatility']:.2f}%")
                self.logger.info(f"    Annualized Volatility: {metrics['annualized_volatility']:.2f}%")
                self.logger.info(f"    Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
                self.logger.info(f"    Max Drawdown: {metrics['max_drawdown']:.2f}%")
        except Exception as e:
            self.logger.error(f"  ✗ Volatility analysis failed: {e}")
        
        # Performance summary
        self.logger.info("\n[5/5] Generating performance summary...")
        try:
            perf = self.analytics.performance_summary(self.symbols)
            report["performance_summary"] = perf
            for symbol, metrics in perf.items():
                self.logger.info(f"  {symbol}: Return={metrics['return']:.2f}%, Vol={metrics['volatility']:.2f}%, WR={metrics['win_rate']:.1f}%")
        except Exception as e:
            self.logger.error(f"  ✗ Performance summary failed: {e}")
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("REPORT GENERATION COMPLETE")
        self.logger.info("=" * 80)
        
        return report

    def save_report_json(self, report: dict) -> Path:
        """Save report as JSON for further analysis."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.log_dir / f"analytics_data_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Report saved to: {report_file}")
        return report_file

    def save_report_csv(self, report: dict) -> Path:
        """Save symbol analysis as CSV."""
        import pandas as pd
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.log_dir / f"analytics_symbols_{timestamp}.csv"
        
        # Convert symbol analysis to CSV
        data = []
        for symbol, analysis in report["symbol_analysis"].items():
            data.append(analysis)
        
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False)
        
        self.logger.info(f"CSV report saved to: {csv_file}")
        return csv_file


if __name__ == "__main__":
    reporter = AnalyticsReporter()
    
    # Generate full report
    report = reporter.generate_full_report()
    
    # Save in multiple formats
    reporter.save_report_json(report)
    reporter.save_report_csv(report)
    
    print("\n✓ Report generation complete!")
    print(f"  Logs saved to: {reporter.log_dir}/")
