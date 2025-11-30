#!/usr/bin/env python3
"""
Daily pipeline runner for Super Agent Trader.
Executes: DataAgent (fetch) → MLAgent (train) → PredictAgent (predict) → Analytics (report)
Runs on schedule via Windows Task Scheduler
"""
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.super_agent import SuperAgent
from utils.analytics_reporter import AnalyticsReporter


def setup_daily_logger():
    """Setup logger for daily runs."""
    log_dir = Path("logs") / "daily_runs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"pipeline_{timestamp}.log"
    
    logger = logging.getLogger("DailyPipeline")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger, log_file


def main():
    """Run daily pipeline."""
    logger, log_file = setup_daily_logger()
    
    try:
        logger.info("=" * 80)
        logger.info("STARTING DAILY PIPELINE")
        logger.info("=" * 80)
        
        # Run super agent pipeline (data fetch → model training → predictions)
        logger.info("\n[PHASE 1/2] Running Super Agent Pipeline...")
        agent = SuperAgent()
        predictions = agent.run_daily()
        logger.info(f"  ✓ Predictions generated: {predictions}")
        
        # Generate analytics report
        logger.info("\n[PHASE 2/2] Generating Analytics Report...")
        reporter = AnalyticsReporter()
        report = reporter.generate_full_report()
        report_json = reporter.save_report_json(report)
        report_csv = reporter.save_report_csv(report)
        logger.info(f"  ✓ JSON Report: {report_json}")
        logger.info(f"  ✓ CSV Report: {report_csv}")
        
        logger.info("\n" + "=" * 80)
        logger.info("DAILY PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Full log: {log_file}")
        
        return 0
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("PIPELINE FAILED")
        logger.error("=" * 80)
        logger.exception(f"Error: {e}")
        logger.error(f"Log file: {log_file}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
