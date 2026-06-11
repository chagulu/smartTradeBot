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
