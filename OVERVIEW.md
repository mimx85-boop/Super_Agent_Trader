Super Agent Trader - Plain English Overview

This project runs a simple, reliable daily routine that:

- Fetches recent end-of-day stock prices from Interactive Brokers (IBKR) for a small set of tickers (AAPL, MSFT, TSLA).
- Calculates basic analytics and produces easy-to-view charts.
- Stores data and visuals in AWS S3 for safekeeping and access.
- Sends a daily email status with a friendly rotating greeting in different languages.

How It Works (At a Glance)

- GitHub Actions (in the cloud) schedules and runs the pipeline every day. You can also trigger it on demand.
- The workflow connects to an EC2 server that runs the IBKR Gateway (headless) so IBKR's API is reachable from the cloud.
- The Python pipeline uses IB's API to pull 1-day OHLC bars with ~30 days lookback, computes metrics, saves files, and emails results.

The Moving Parts

- Workflow & Scheduling: GitHub Actions (cron + manual dispatch)
- IBKR Access: An Ubuntu EC2 instance runs IBKR Gateway via IBC (a helper that automates login and keeps the gateway alive)
  - Service name: tws-gateway (systemd)
  - Listens on TCP port 4001 for API connections
- Pipeline Code (Python):
  - Entry points: run_daily_pipeline.py, main.py
  - Agents: agents/ coordinate data and predictions
  - IBKR client: utils/ibkr_client.py via ib-insync
  - Storage: utils/s3_client.py uploads to your S3 bucket
  - Analytics & visuals: utils/analytics_reporter.py, visualizations/*.html
- Notifications:
  - Email on success/failure using Gmail SMTP (with an app password)
  - A daily multilingual greeting added at the top of the email

Daily Flow (Step-by-Step)

1. GitHub Actions starts on schedule.
2. Secrets (like IBKR host/port, AWS keys, email) are loaded and a config file is generated.
3. The job connects to the IBKR Gateway on EC2 at IBKR_HOST:IBKR_PORT (port 4001).
4. It fetches ~30 days of 1-day candles for the configured tickers.
5. It computes basic analytics, writes CSV/JSON and charts, and uploads to S3.
6. It sends a status email with the rotating greeting and key results.

How To Tell It's Working

- On EC2 (as ubuntu):
  - sudo systemctl status tws-gateway --no-pager (service should be active)
  - sudo ss -ltnp | grep 4001 (should show LISTEN on 0.0.0.0:4001 by a Java process)
  - sudo journalctl -u tws-gateway -f (live logs; confirms login and startup)
- In GitHub:
  - Actions tab shows runs and logs
  - Secrets include IBKR_HOST (EC2 public IP) and IBKR_PORT (4001)
- From your PC (Windows PowerShell):
  - Test-NetConnection -ComputerName <EC2_IP> -Port 4001 (should return TcpTestSucceeded : True)

Common Gotchas (Quick Fixes)

- Too many login attempts -> IBKR enforces a short lockout (~5 minutes). Wait, then it will retry.
- Port not listening -> Ensure xterm is installed, the service uses xvfb-run, and ExecStart points to the correct IBC launcher.
- Connection refused in Actions -> Confirm security group allows inbound TCP 4001 and that GitHub secrets have the current EC2 IP.
- Email failures -> Use a Gmail app password (2FA required), not your normal Gmail password.

Security Notes

- Never commit secrets. Store them in GitHub Secrets and on EC2 (IBC config) securely.
- Limit who can SSH to the EC2 instance and who can edit GitHub Secrets.

Where To Learn More

- PROJECT_SUMMARY_AND_DOCUMENTATION.md — Full end-to-end documentation
- EC2_TWS_SETUP.md — How the EC2 + IBKR Gateway is installed
- README.md — Quick start and repository overview

That's it — one daily job that fetches market data, saves it, makes charts, and emails you a simple update.