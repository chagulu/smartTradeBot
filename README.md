# SmartTradeBot

EMA Conditional Strategy Engine backend for Zerodha Kite Connect.

## Overview

This Python application provides a Flask API, strategy engine, market data integration, and worker scheduler for automated EMA-based trading.

## Architecture

- `app.py` - Flask API layer
- `smart_trade_bot/` - core modules
  - `auth.py` - Zerodha authentication and token storage
  - `market_data.py` - LTP and historical data retrieval via Kite Connect
  - `strategy_engine.py` - EMA-based entry and multi-stage profit booking exit logic
  - `order_execution.py` - place / modify / cancel orders
  - `worker.py` - periodic strategy evaluation engine
  - `storage.py` - SQLite storage for tokens, positions, and strategies

## Installation

1. Create a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables:

```bash
export SMARTTRADEBOT_API_KEY="your_api_key"
export SMARTTRADEBOT_API_SECRET="your_api_secret"
export SMARTTRADEBOT_SECRET_KEY="a_random_flask_secret"
```

3. Run the app:

```bash
python app.py
```

## API Endpoints

- `POST /auth/login` - save Zerodha access token
- `GET /strategy/status` - get active strategy status
- `POST /strategy/activate` - activate a strategy
- `POST /strategy/deactivate` - deactivate a strategy
- `GET /worker/health` - worker health check

## Notes

This implementation is a starting point and uses placeholders for Kite Connect order execution and strategy values. Customize the strategy parameters and risk management before using with a live trading account.
