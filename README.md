# SmartTradeBot - EMA Strategy Engine Development Specification

## Project Overview

Develop an automated trading engine integrated with Zerodha Kite Connect APIs.

The system should support:

* Zerodha authentication
* Strategy management
* Automated buy execution
* Multi-stage sell execution
* Portfolio tracking
* Order tracking
* Background execution engine
* Risk management controls

---

# Technology Stack

Backend:

* Python 3.12+
* Flask
* SQLAlchemy
* MySQL 8+

Broker Integration:

* Zerodha Kite Connect

Scheduler:

* APScheduler (initial implementation)
* Celery + Redis (future enhancement)

Frontend:

* HTML/Jinja or React

---

# Database Tables

## users

Purpose:
Store application users and Zerodha mapping.

Columns:

* id (INT PK AUTO_INCREMENT)
* email
* zerodha_user_id
* zerodha_access_token
* created_at
* updated_at

---

## ema_strategies

Purpose:
Store strategy configurations.

Columns:

* id
* user_id (FK users.id)
* symbol
* ema_period (default 100)

Buy Window:

* buy_time_start (default 15:15)
* buy_time_end (default 15:30)

Sell Configuration:

* stage_1_profit_percent (default 10)
* stage_2_profit_percent (default 20)
* stage_3_profit_percent (default 30)

Risk Controls:

* stop_loss_percent (default 15)
* max_position_size
* max_capital_allocation
* max_daily_loss

Execution State:

* current_position_quantity
* current_position_avg_price

Stage Tracking:

* stage_1_completed
* stage_2_completed
* stage_3_completed

System Fields:

* status (ACTIVE / PAUSED)
* is_active
* created_at
* updated_at

---

## execution_logs

Purpose:
Track all buy/sell executions.

Columns:

* id
* strategy_id
* action (BUY / SELL)
* symbol
* quantity
* price
* broker_order_id
* remarks
* created_at

---

# Buy Strategy

## Entry Condition

Generate BUY signal when:

Daily candle closes below EMA(N)

Where:

N = user-configurable EMA period
Default = 100

Condition:

daily_close &lt; EMA(period)

AND

current_time between buy_time_start and buy_time_end

AND

current_position_quantity = 0

THEN

Place BUY order.

---

# Buy Order Rules

Order Type:
MARKET

Product:
CNC

Variety:
regular

Quantity:
Calculated based on:

* max_position_size
* max_capital_allocation

---

# Position Tracking

The system must support multiple buys over time.

Example:

Lot 1:
Price = 180
Qty = 100

Lot 2:
Price = 200
Qty = 50

Lot 3:
Price = 160
Qty = 75

Lot 4:
Price = 120
Qty = 75

Total Quantity:

300

Weighted Average Price:

(180×100 + 200×50 + 160×75 + 120×75) / 300

Average Price = 163.33

Store this value in:

current_position_avg_price

---

# Sell Strategy

Use weighted average price.

---

## Sell Stage 1

Trigger:

market_price &gt;= average_price × 1.10

Action:

Sell 50% of current position.

Mark:

stage_1_completed = TRUE

Log execution.

---

## Sell Stage 2

Trigger:

market_price &gt;= average_price × 1.20

Action:

Sell 50% of remaining quantity.

Mark:

stage_2_completed = TRUE

Log execution.

---

## Sell Stage 3

Trigger:

market_price &gt;= average_price × 1.30

Action:

Sell all remaining shares.

Mark:

stage_3_completed = TRUE

Reset position tracking.

Log execution.

---

# Stop Loss

Trigger:

market_price &lt;= average_price × (1 - stop_loss_percent)

Action:

Sell all remaining shares.

Pause strategy execution for that symbol.

Log execution.

---

# Strategy Execution Engine

Create a background worker.

Execution frequency:

Every 5 seconds.

Process:

1. Load all ACTIVE strategies.
2. Fetch market data.
3. Evaluate BUY conditions.
4. Evaluate SELL conditions.
5. Execute broker orders.
6. Update database state.
7. Write execution logs.

---

# APIs

## POST /api/strategies

Create strategy.

---

## GET /api/strategies

List strategies.

---

## GET /api/strategies/{id}

Get strategy details.

---

## PUT /api/strategies/{id}

Update strategy.

---

## POST /api/strategies/{id}/activate

Activate strategy.

---

## POST /api/strategies/{id}/pause

Pause strategy.

---

## DELETE /api/strategies/{id}

Delete strategy.

---

## GET /api/executions

Execution history.

---

# Dashboard Requirements

Display:

* Active strategies
* Current positions
* Average purchase price
* Current market price
* Unrealized P&L
* Stage 1 status
* Stage 2 status
* Stage 3 status
* Last execution timestamp

---

# Logging Requirements

Log the following:

* Strategy created
* Strategy updated
* Buy condition satisfied
* Buy order placed
* Sell stage 1 executed
* Sell stage 2 executed
* Sell stage 3 executed
* Stop loss triggered
* Broker API failures

---

# Error Handling

Handle:

* Invalid symbols
* Market closed
* Insufficient funds
* Zerodha authentication failure
* Order rejection
* Duplicate execution prevention

---

# Future Enhancements

Phase 2:

* WebSocket price streaming
* Paper trading mode
* RSI confirmation
* Trailing stop-loss
* Telegram notifications
* Email notifications
* Strategy backtesting
* Multi-broker support
* Portfolio analytics

---

# Acceptance Criteria

The feature is complete when:

* Strategies can be created through UI/API.
* Buy orders execute only when EMA and time conditions match.
* Weighted average price is correctly calculated.
* Three-stage selling executes correctly.
* Stop loss executes correctly.
* All executions are logged.
* Dashboard reflects live strategy state.
* No duplicate order executions occur.

End of Specification.
