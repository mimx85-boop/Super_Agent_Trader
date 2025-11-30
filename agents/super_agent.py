from .base_agent import BaseAgent
from .data_agent import DataAgent
from .ml_agent import MLAgent
from .predict_agent import PredictAgent


class SuperAgent(BaseAgent):
    """Orchestrates the data, ML, and prediction agents in sequence."""

    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(config_path)
        self.data_agent = DataAgent(config_path)
        self.ml_agent = MLAgent(config_path)
        self.predict_agent = PredictAgent(config_path)

    def run_daily(self):
        self.logger.info("Step 1: Updating data from IBKR → S3")
        self.data_agent.run()

        self.logger.info("Step 2: Training / updating models")
        self.ml_agent.run()

        self.logger.info("Step 3: Running predictions")
        results = self.predict_agent.run()
        self.logger.info(f"Final prediction snapshot: {results}")
