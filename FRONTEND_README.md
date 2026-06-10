# SmartTradeBot Frontend Development Guide

## Project Overview

Build a responsive frontend dashboard for SmartTradeBot, an algorithmic trading platform integrated with Zerodha Kite Connect.

The frontend should interact with the existing Flask backend APIs.

---

# Technology Stack

Preferred:

* React 19+
* TypeScript
* Vite
* Tailwind CSS
* Axios
* React Router
* React Hook Form
* Recharts

Alternative:

* HTML + Bootstrap + Vanilla JavaScript

---

# Backend URL

Development:

```text
http://localhost:5001
```

---

# Authentication Flow

Current Backend Implementation:

User logs into Zerodha manually.

Frontend should:

1. Redirect user to Zerodha login URL.
2. Capture request_token from callback URL.
3. Call backend login API.

---

# Authentication APIs

## Login

Endpoint:

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

Response:

```json
{
    "message": "login_successful",
    "user_id": "UPP323",
    "access_token": "...",
    "session_data": {}
}
```

Store:

```text
user_id
login status
```

Do NOT expose access token in UI.

---

# Health API

## Worker Status

Endpoint:

```http
GET /worker/health
```

Response:

```json
{
    "status": "ok",
    "interval_seconds": 15
}
```

Display:

```text
Worker Status: Running
Evaluation Interval: 15 seconds
```

---

# Strategy APIs

## Get Strategy Status

Endpoint:

```http
GET /strategy/status
```

Response Example:

```json
{
    "active_strategies": [
        {
            "id": 1,
            "symbol": "INFY",
            "ema_period": 100,
            "quantity": 100,
            "entry_buffer_percent": 0.0,
            "profit_targets": [0.10, 0.20, 0.30],
            "stop_loss": 0.15
        }
    ]
}
```

Display:

* Symbol
* EMA Period
* Quantity
* Strategy Status (Active)
* Action (Deactivate Strategy ID)

---

## Activate Strategy

Endpoint:

```http
POST /strategy/activate
```

Payload:

```json
{
    "symbol": "INFY",
    "ema_period": 100,
    "quantity": 100,
    "entry_buffer_percent": 0.0,
    "profit_targets": [0.10, 0.20, 0.30],
    "stop_loss": 0.15
}
```

Response:

```json
{
    "message": "strategy_activated",
    "strategy_id": 1
}
```

---

## Deactivate Strategy

Endpoint:

```http
POST /strategy/deactivate
```

Payload:

```json
{
    "strategy_id": 1
}
```

Response:

```json
{
    "message": "strategy_deactivated",
    "strategy_id": 1
}
```

---

# Frontend Pages

---

## Login Page

Route:

```text
/login
```

Features:

* Zerodha Login button
* Request Token input field
* User ID field

Actions:

Submit login payload to backend.

---

## Dashboard

Route:

```text
/
```

Widgets:

* Worker Health Status
* Active Strategies List
* Position Summary
* Quick Actions

---

## Strategy Management

Route:

```text
/strategies
```

Features:

* Activate Strategy
* Deactivate Strategy
* View Active Strategies

---

# Activate Strategy Form

Fields:

```text
Symbol
EMA Period
Quantity
Entry Buffer %
Profit Targets % (can be comma-separated or dynamic fields)
Stop Loss %
```

Validation:

```text
Symbol is required
EMA > 0
Quantity > 0
Profit Targets > 0
Stop Loss > 0
```

---

# Dashboard Layout

Header:

```text
SmartTradeBot
Logged In User
Logout Button
```

Sidebar:

```text
Dashboard
Strategies
Health Monitor
```

Main Content:

```text
Worker Health Card
Active Strategies Card
```

---

# Worker Health Card

Display:

```text
Status
Evaluation Interval
```

Example:

```text
Running
15 Seconds
```

---

# Strategy Status Card

Display:

```text
Strategy ID
Symbol
EMA Period
Quantity
Profit Targets
Stop Loss
Actions: Deactivate Button
```

---

# State Management

Use React Context.

Global State:

```typescript
interface AppState {
    userId: string;
    loggedIn: boolean;
    workerStatus: string;
    activeStrategies: Strategy[];
}
```

---

# Axios Configuration

Base URL:

```typescript
http://localhost:5001
```

Default Headers:

```typescript
Content-Type: application/json
```

---

# Error Handling

Show toast notifications for:

```text
Login Failure
Strategy Activation Failure
Worker Offline
API Timeout
```

---

# Loading States

Display spinner while:

```text
Authenticating
Fetching Worker Status
Activating Strategy
Fetching Strategy Status
```

---

# Polling

Refresh worker health every:

```text
30 seconds
```

Refresh strategy status every:

```text
15 seconds
```

---

# Folder Structure

```text
src/
  components/
  pages/
  services/
  hooks/
  context/
  types/
  utils/
```

---

# Components

```text
Header
Sidebar
WorkerHealthCard
StrategyListCard
StrategyForm
Loader
ToastNotification
```

---

# Services

```text
authService.ts
strategyService.ts
workerService.ts
```

---

# TypeScript Interfaces

```typescript
interface WorkerHealth {
    status: string;
    interval_seconds: number;
}

interface Strategy {
    id: number;
    symbol: string;
    ema_period: number;
    quantity: number;
    entry_buffer_percent: number;
    profit_targets: number[];
    stop_loss: number;
}
```

---

# Acceptance Criteria

The frontend is complete when:

* User can log in.
* Worker health is displayed.
* Strategy status is displayed accurately.
* Strategy activation works with appropriate payload structure.
* Strategy deactivation works via strategy ID.
* Errors are handled gracefully.
* Dashboard is responsive.

---

# Future Enhancements

Phase 2:

* Portfolio Page
* Order History
* Live Market Data
* Real-Time WebSocket Updates
* Multiple Strategies
* Notifications
* Dark Mode
* Paper Trading
* Backtesting
* Multi-Broker Support
