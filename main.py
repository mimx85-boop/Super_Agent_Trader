from agents.super_agent import SuperAgent

if __name__ == "__main__":
    sa = SuperAgent("config.yaml")
    sa.run_daily()
