# SmartTradeBot – Conditional Trading Engine

## Functional & Technical Development Specification (Version 2.0)

---

# 1. Project Overview

SmartTradeBot is a Zerodha-integrated automated trading platform that allows users to:

* Place manual orders.
* Create conditional orders.
* Execute EMA-based automated strategies.
* Track portfolio and positions.
* Monitor order execution status.
* Automate profit booking through staged exits.

---

# 2. Core Modules

The system shall consist of the following modules:

1. Authentication Module
2. Dashboard Module
3. Portfolio Module
4. Order Management Module
5. Conditional Order Engine
6. EMA Strategy Engine
7. Worker Engine
8. Execution Engine
9. Notification Engine
10. Audit & Reporting Module

---

# 3. Authentication Module

Broker: Zerodha Kite Connect

### Features

* Login via Zerodha.
* Request token exchange.
* Access token storage.
* Session management.
* Logout.

---

# 4. Dashboard Module

URL:

```
/dashboard
```

Displays:

### Worker Status

* Running
* Stopped
* Last execution time

### Portfolio Summary

* Holdings
* Positions
* Today's P&L
* Total Investment

### Live Orders

Display:

| Symbol | Type | Qty | Status | Price |

Statuses:

* OPEN
* COMPLETE
* REJECTED
* CANCELLED

### User Profile

Display:

* User Name
* Email
* Zerodha Client ID

---

# 5. Manual Order Module

User can place:

### BUY Order

Inputs:

* Symbol
* Quantity

### SELL Order

Inputs:

* Symbol
* Quantity

Execution:

```
Frontend
↓
POST /orders/place
↓
OrderExecutor
↓
Kite Connect
↓
Exchange
```

---

# 6. Conditional Order Engine

URL:

```
/conditional-orders
```

Purpose:

Queue orders until conditions become true.

---

# 7. Conditional Order Types

Supported conditions:

### PRICE_ABOVE

Example:

```
BUY INFY
when price > 1800
```

---

### PRICE_BELOW

Example:

```
BUY INFY
when price < 1700
```

---

### EMA_BELOW

Example:

```
BUY INFY
when Daily Close < EMA(100)
```

---

### EMA_ABOVE

Example:

```
SELL INFY
when Daily Close > EMA(100)
```

---

# 8. Conditional Order States

Status values:

```
WAITING
TRIGGERED
EXECUTED
CANCELLED
FAILED
```

---

# 9. Conditional Order Inputs

| Field          | Required |
| -------------- | -------- |
| Symbol         | Yes      |
| Action         | Yes      |
| Condition      | Yes      |
| Quantity       | Yes      |
| Trigger Price  | Optional |
| EMA Period     | Optional |
| Buy Start Time | Optional |
| Buy End Time   | Optional |

---

# 10. EMA Entry Strategy

Buy Condition:

```
Daily Close < EMA(100)
```

AND

```
15:15 ≤ Current Time ≤ 15:30
```

---

Default:

```
EMA = 100
Buy Start = 15:15
Buy End = 15:30
```

---

# 11. Position Tracking

Track every buy.

Example:

| Price | Qty |
| ----- | --- |
| 180   | 100 |
| 200   | 50  |
| 160   | 75  |
| 120   | 75  |

---

# 12. Average Price Calculation

Formula:

```
Average Price =
Σ(Buy Price × Quantity)
÷
Σ(Quantity)
```

Example:

```
(180×100)+(200×50)+(160×75)+(120×75)

=

49,000

÷

300

=

163.33
```

---

# 13. Profit Booking Engine

Stage 1:

```
Average Price + 10%
```

Sell:

```
50% of total quantity
```

---

Stage 2:

```
Average Price + 20%
```

Sell:

```
50% of remaining quantity
```

---

Stage 3:

```
Average Price + 30%
```

Sell:

```
All remaining quantity
```

---

# 14. Stop Loss Engine

Trigger:

```
Average Price − Stop Loss %
```

Default:

```
15%
```

Action:

```
Sell entire remaining position.
```

---

# 15. Worker Engine

Runs every:

```
15 seconds
```

Workflow:

```
Load waiting orders

FOR each order

    Get market data

    Evaluate condition

    IF TRUE

        Execute order

        Update status

END
```

---

# 16. Market Data Module

Uses:

```
kite.ltp()
kite.historical_data()
```

Future:

```
KiteTicker WebSocket
```

---

# 17. Database Tables

## users

```
id
zerodha_user_id
email
created_at
updated_at
```

---

## conditional_orders

```
id
user_id
symbol
action
condition_type
trigger_price
ema_period
quantity
status
created_at
updated_at
executed_at
```

---

## positions

```
id
user_id
symbol
quantity
average_price
invested_amount
current_pnl
created_at
updated_at
```

---

## executions

```
id
order_id
symbol
action
quantity
price
stage
kite_order_id
executed_at
```

---

## ema_strategies

```
id
user_id
symbol
ema_period
buy_time_start
buy_time_end
stage_1_profit_percent
stage_2_profit_percent
stage_3_profit_percent
stop_loss_percent
status
created_at
updated_at
```

---

# 18. APIs

Authentication:

```
GET  /auth/login
GET  /auth/callback
POST /auth/logout
```

Dashboard:

```
GET /dashboard
GET /portfolio
GET /orders/live
```

Conditional Orders:

```
POST /conditional-orders
GET  /conditional-orders
DELETE /conditional-orders/{id}
```

Strategies:

```
POST /strategy/activate
POST /strategy/deactivate
GET  /strategy/status
```

Worker:

```
GET /worker/health
```

Orders:

```
POST /orders/place
POST /orders/cancel
```

---

# 19. Frontend Pages

```
/login
/dashboard
/orders
/conditional-orders
/portfolio
/profile
```

---

# 20. Notification Engine

Future Support:

* Telegram Alerts
* Email Alerts
* Push Notifications

Events:

```
Order Executed
Conditional Triggered
Stop Loss Hit
Profit Booked
Worker Failure
```

---

# 21. Audit Requirements

Log:

```
Login
Logout
Order Creation
Order Execution
Strategy Activation
Strategy Deactivation
Worker Execution
Errors
```

---

# 22. Future Roadmap

Phase 2:

```
KiteTicker WebSocket
Paper Trading
Backtesting
Multi-user Support
Multi-stock Scanner
Trailing Stop Loss
```

Phase 3:

```
AI Signal Generation
Portfolio Optimization
Risk Scoring
ML-based Exit Engine
```

---

# 23. Acceptance Criteria

The system is complete when:

✓ User logs in successfully.

✓ Manual orders execute.

✓ Conditional orders trigger correctly.

✓ EMA strategy triggers correctly.

✓ Multi-stage selling works.

✓ Stop loss works.

✓ Worker executes every interval.

✓ Dashboard reflects live state.

✓ Audit logs are maintained.

✓ Notifications are generated.

---

# 24. Recommended Redevelopment Approach

Build in this order:

1. Authentication
2. Dashboard
3. Manual Orders
4. Conditional Order Engine
5. Position Tracking
6. Worker Engine
7. EMA Strategy Engine
8. Profit Booking Engine
9. Notifications
10. Backtesting

```
```


# SmartTradeBot Backend Changes Required

This file documents the Python/Flask backend changes needed to support the completed React frontend for EMA Strategy v2.

Frontend base URL:

```text
http://localhost:5001
```

All JSON APIs should return `Content-Type: application/json`.

---

## 1. CORS

Allow the Vite frontend origin during development:

```text
http://localhost:5173
```

Required methods:

```text
GET, POST, OPTIONS
```

Required headers:

```text
Content-Type
```

---

## 2. Authentication

### Zerodha Login Redirect

Frontend button opens:

```http
GET /auth/login
```

Backend should redirect the user to Zerodha Kite login.

After Zerodha login, backend should send the browser back to the frontend with query params if possible:

```text
http://localhost:5173/login?request_token=<token>&user_id=<zerodha_user_id>
```

If `user_id` is not known at redirect time, the frontend still allows manual entry.

### Token Exchange

Frontend calls:

```http
POST /auth/login
```

Payload:

```json
{
  "request_token": "generated_by_zerodha",
  "user_id": "UPP323"
}
```

Expected success response:

```json
{
  "message": "login_successful",
  "user_id": "UPP323",
  "access_token": "...",
  "session_data": {}
}
```

Notes:

- Frontend stores only `user_id` and `loggedIn`.
- Frontend does not display the access token.
- Backend should return a non-2xx response with an `error` message on login failure.

---

## 3. Worker Health

Frontend polls every 30 seconds:

```http
GET /worker/health
```

Expected response:

```json
{
  "status": "ok",
  "interval_seconds": 15
}
```

Frontend treats `status: "ok"` or `status: "running"` as Running. Any failed request is shown as Offline.

Recommended backend behavior:

- Return HTTP `200` if the worker process/check loop is healthy.
- Return HTTP `503` if the worker is unavailable.
- Include `interval_seconds` from the actual worker configuration.

---

## 4. EMA Strategy Activation

Frontend calls:

```http
POST /strategy/activate
```

Payload:

```json
{
  "symbol": "INFY",
  "ema_period": 100,
  "buy_time_start": "15:15",
  "buy_time_end": "15:30",
  "stage_1_profit_percent": 10,
  "stage_2_profit_percent": 20,
  "stage_3_profit_percent": 30,
  "stop_loss_percent": 15,
  "max_position_size": 1000,
  "max_capital_allocation": 50000,
  "max_daily_loss": 5000
}
```

Expected response:

```json
{
  "message": "strategy_activated",
  "strategy_id": 1
}
```

Required backend validation:

- `symbol` is required and should be normalized to uppercase.
- `ema_period > 0`.
- `buy_time_start` and `buy_time_end` are required in `HH:MM` format.
- `buy_time_end > buy_time_start`.
- `stage_1_profit_percent > 0`.
- `stage_2_profit_percent > stage_1_profit_percent`.
- `stage_3_profit_percent > stage_2_profit_percent`.
- `stop_loss_percent > 0`.
- `max_position_size > 0`.
- `max_capital_allocation > 0`.
- `max_daily_loss > 0`.

Recommended failure response:

```json
{
  "error": "validation_failed",
  "details": {
    "ema_period": "EMA period must be greater than 0"
  }
}
```

Use HTTP `400` for validation errors.

---

## 5. Strategy Status

Frontend polls every 15 seconds:

```http
GET /strategy/status
```

Expected response:

```json
{
  "active_strategies": [
    {
      "id": 1,
      "symbol": "INFY",
      "ema_period": 100,
      "buy_time_start": "15:15",
      "buy_time_end": "15:30",
      "stage_1_profit_percent": 10,
      "stage_2_profit_percent": 20,
      "stage_3_profit_percent": 30,
      "stop_loss_percent": 15,
      "max_position_size": 1000,
      "max_capital_allocation": 50000,
      "max_daily_loss": 5000,
      "current_position_quantity": 250,
      "current_position_avg_price": 163.33,
      "total_pnl": 5400,
      "status": "ACTIVE",
      "stage_1_completed": true,
      "stage_2_completed": false,
      "stage_3_completed": false
    }
  ]
}
```

Required fields for every strategy object:

```text
id
symbol
ema_period
buy_time_start
buy_time_end
stage_1_profit_percent
stage_2_profit_percent
stage_3_profit_percent
stop_loss_percent
max_position_size
max_capital_allocation
max_daily_loss
current_position_quantity
current_position_avg_price
total_pnl
status
stage_1_completed
stage_2_completed
stage_3_completed
```

Allowed `status` values:

```text
ACTIVE
PAUSED
STOPPED
COMPLETED
```

Frontend derives dashboard values from this response:

- Total active strategies: count where `status === "ACTIVE"`.
- Total quantity held: sum of `current_position_quantity`.
- Total capital utilized: sum of `current_position_quantity * current_position_avg_price`.
- Total unrealized P&L: sum of `total_pnl`.
- Recent activity: first 5 strategies from `active_strategies`.

Backend should return an empty array when no strategies exist:

```json
{
  "active_strategies": []
}
```

---

## 6. Strategy Deactivate

Frontend calls after confirmation:

```http
POST /strategy/deactivate
```

Payload:

```json
{
  "strategy_id": 1
}
```

Expected response:

```json
{
  "message": "strategy_deactivated",
  "strategy_id": 1
}
```

Recommended backend behavior:

- Mark strategy as `STOPPED`.
- Stop worker evaluation for that strategy.
- Do not delete historical strategy/order data.
- Return HTTP `404` if `strategy_id` does not exist.

---

## 7. Strategy Pause

The frontend has a Pause button for active strategies.

Frontend calls:

```http
POST /strategy/pause
```

Payload:

```json
{
  "strategy_id": 1
}
```

Expected response:

```json
{
  "message": "strategy_paused",
  "strategy_id": 1
}
```

Recommended backend behavior:

- Only allow pause when `status === "ACTIVE"`.
- Change status to `PAUSED`.
- Worker should skip new evaluation/execution for paused strategies.
- Existing positions should remain visible in `/strategy/status`.

Recommended error responses:

- HTTP `404` if strategy does not exist.
- HTTP `409` if strategy cannot be paused from its current state.

---

## 8. Strategy Resume

The frontend has a Resume button for paused strategies.

Frontend calls:

```http
POST /strategy/resume
```

Payload:

```json
{
  "strategy_id": 1
}
```

Expected response:

```json
{
  "message": "strategy_resumed",
  "strategy_id": 1
}
```

Recommended backend behavior:

- Only allow resume when `status === "PAUSED"`.
- Change status to `ACTIVE`.
- Worker should resume evaluation on its next cycle.

Recommended error responses:

- HTTP `404` if strategy does not exist.
- HTTP `409` if strategy cannot be resumed from its current state.

---

## 9. Database / Model Fields

The strategy persistence model should include at least:

```text
id
symbol
ema_period
buy_time_start
buy_time_end
stage_1_profit_percent
stage_2_profit_percent
stage_3_profit_percent
stop_loss_percent
max_position_size
max_capital_allocation
max_daily_loss
current_position_quantity
current_position_avg_price
total_pnl
status
stage_1_completed
stage_2_completed
stage_3_completed
created_at
updated_at
```

Recommended defaults:

```text
status = ACTIVE
current_position_quantity = 0
current_position_avg_price = 0
total_pnl = 0
stage_1_completed = false
stage_2_completed = false
stage_3_completed = false
```

---

## 10. Worker Logic Changes

Worker should:

- Evaluate only strategies where `status === "ACTIVE"`.
- Ignore strategies where `status === "PAUSED"` or `status === "STOPPED"`.
- Update `current_position_quantity`, `current_position_avg_price`, and `total_pnl`.
- Mark `stage_1_completed`, `stage_2_completed`, and `stage_3_completed` when staged exits are executed.
- Mark strategy `COMPLETED` when all exit stages are complete and no active position remains.
- Respect `max_position_size`, `max_capital_allocation`, and `max_daily_loss`.
- Respect the configured buy window: `buy_time_start <= current_time <= buy_time_end`.

---

## 11. Error Response Shape

Use a consistent JSON error format for frontend toast handling:

```json
{
  "error": "human_or_machine_readable_error",
  "message": "Optional readable message"
}
```

Recommended status codes:

```text
400 validation error
401 unauthenticated/session expired
404 strategy not found
409 invalid strategy state transition
500 unexpected backend error
503 worker offline
```

---

## 12. Frontend API Checklist

The backend is compatible with the current frontend when these endpoints work:

```text
GET  /auth/login
POST /auth/login
GET  /worker/health
GET  /strategy/status
POST /strategy/activate
POST /strategy/deactivate
POST /strategy/pause
POST /strategy/resume
```

Minimum manual test flow:

1. Start backend on `http://localhost:5001`.
2. Start frontend on `http://localhost:5173`.
3. Login through Zerodha or submit a valid request token manually.
4. Open `/strategies`.
5. Activate an EMA strategy with all fields.
6. Confirm `/strategy/status` returns the full strategy object.
7. Pause the strategy.
8. Resume the strategy.
9. Deactivate the strategy.
10. Confirm dashboard cards update from strategy status polling.
