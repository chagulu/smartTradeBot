# SmartTradeBot – EMA Based Conditional Trading Strategy

## Functional Specification & Business Requirements Document (Version 1.0)

---

# 1. Document Information

| Item             | Details                                    |
| ---------------- | ------------------------------------------ |
| Project          | SmartTradeBot                              |
| Module           | EMA Conditional Strategy Engine            |
| Version          | 1.0                                        |
| Prepared By      | Basanta Kumar Swain                        |
| Technology Stack | Python, Flask, React, Zerodha Kite Connect |
| Broker           | Zerodha                                    |
| Scheduler        | APScheduler                                |
| Database         | MySQL                                      |
| Last Updated     | June 2026                                  |

---

# 2. Objective

Develop an automated trading system capable of:

1. Monitoring stocks continuously.
2. Identifying buying opportunities using EMA-based conditions.
3. Executing buy orders automatically during predefined market timings.
4. Managing exits using staged profit booking.
5. Calculating weighted average purchase prices dynamically.
6. Maintaining execution history and performance metrics.

---

# 3. Strategy Overview

The strategy consists of two major components:

### Entry Engine

Responsible for identifying buying opportunities.

### Exit Engine

Responsible for staged profit booking.

---

# 4. Buying Strategy

## 4.1 Buy Criteria

A buy signal shall be generated when:

```text
Daily candle closes below configured EMA.
```

---

## 4.2 EMA Configuration

| Parameter   | Value        |
| ----------- | ------------ |
| EMA Period  | Configurable |
| Default EMA | 100          |

Example:

```text
EMA(100)
```

---

## 4.3 Entry Time Window

Orders shall only be placed during a configurable time window.

Default values:

| Parameter      | Value |
| -------------- | ----- |
| Buy Start Time | 15:15 |
| Buy End Time   | 15:30 |

Example:

```text
15:15 PM ≤ Current Time ≤ 15:30 PM
```

---

## 4.4 Buy Execution Logic

Buy order shall be executed only if:

```text
Condition 1:
Daily candle closes below EMA.

AND

Condition 2:
Current market time falls within buy window.

AND

Condition 3:
Strategy is active.

AND

Condition 4:
Risk limits are not breached.
```

---

# 5. Position Accumulation

The strategy supports multiple buy executions.

Example:

| Purchase Price | Quantity |
| -------------- | -------- |
| ₹180           | 100      |
| ₹200           | 50       |
| ₹160           | 75       |
| ₹120           | 75       |

---

# 6. Weighted Average Price Calculation

Average purchase price shall be calculated as:

```text
Average Price =
Σ(Buy Price × Quantity)
÷
Σ(Quantity)
```

---

## Example

```text
(180×100 + 200×50 + 160×75 + 120×75)

=

49,000
```

Total Quantity:

```text
300
```

Average Price:

```text
163.33
```

---

# 7. Selling Strategy

Profit booking shall occur in three stages.

---

# Stage 1 Exit

## Trigger

```text
Average Price + 10%
```

---

## Quantity

```text
50% of total available quantity.
```

---

## Example

Average Price:

```text
163.33
```

Target:

```text
163.33 × 1.10

=

179.66
```

Quantity Sold:

```text
150 Shares
```

---

# Stage 2 Exit

## Trigger

```text
Average Price + 20%
```

---

## Quantity

```text
50% of remaining quantity.
```

Remaining Quantity:

```text
150 Shares
```

Quantity Sold:

```text
75 Shares
```

Target:

```text
163.33 × 1.20

=

196.00
```

---

# Stage 3 Exit

## Trigger

```text
Average Price + 30%
```

---

## Quantity

```text
All remaining quantity.
```

Remaining Quantity:

```text
75 Shares
```

Target:

```text
163.33 × 1.30

=

212.33
```

---

# 8. Exit Sequence Example

| Stage   | Trigger  | Quantity  |
| ------- | -------- | --------- |
| Stage 1 | Avg +10% | 150       |
| Stage 2 | Avg +20% | 75        |
| Stage 3 | Avg +30% | Remaining |

---

# 9. Risk Management

The system shall enforce the following controls.

---

## Stop Loss

| Parameter | Default |
| --------- | ------- |
| Stop Loss | 15%     |

Logic:

```text
Sell entire position if price falls below average price by configured percentage.
```

---

## Maximum Position Size

| Parameter        | Default     |
| ---------------- | ----------- |
| Maximum Quantity | 1000 Shares |

---

## Maximum Capital Allocation

| Parameter          | Default |
| ------------------ | ------- |
| Capital Allocation | ₹50,000 |

---

## Maximum Daily Loss

| Parameter        | Default |
| ---------------- | ------- |
| Daily Loss Limit | ₹5,000  |

---

# 10. Strategy Status

Each strategy shall maintain the following states.

| Status    |
| --------- |
| ACTIVE    |
| PAUSED    |
| STOPPED   |
| COMPLETED |

---

# 11. Worker Engine

A background worker shall execute periodically.

---

## Frequency

```text
Every 15 Seconds
```

Configurable:

```text
SMARTTRADEBOT_SCHEDULE_INTERVAL_SECONDS
```

---

# 12. Worker Processing Flow

```text
FOR EACH ACTIVE STRATEGY

    Retrieve Market Data

    Evaluate Buy Conditions

    IF Buy Conditions True

        Place Buy Order

        Update Position

    END IF

    Calculate Average Price

    Evaluate Stage 1 Target

    Evaluate Stage 2 Target

    Evaluate Stage 3 Target

    Evaluate Stop Loss

    Execute Orders

    Update Metrics

END FOR
```

---

# 13. Database Table

Table Name:

```text
ema_strategies
```

---

## Fields

| Column                     |
| -------------------------- |
| id                         |
| user_id                    |
| symbol                     |
| ema_period                 |
| buy_time_start             |
| buy_time_end               |
| stage_1_profit_percent     |
| stage_2_profit_percent     |
| stage_3_profit_percent     |
| stop_loss_percent          |
| max_position_size          |
| max_capital_allocation     |
| max_daily_loss             |
| is_active                  |
| status                     |
| current_position_quantity  |
| current_position_avg_price |
| execution_history          |
| total_buy_orders           |
| total_sell_orders          |
| total_pnl                  |
| last_activity_at           |
| created_at                 |
| updated_at                 |

---

# 14. Execution History

The system shall maintain complete execution history.

Examples:

```json
[
    {
        "type":"BUY",
        "price":180,
        "quantity":100
    },
    {
        "type":"SELL",
        "price":179.66,
        "quantity":150,
        "stage":"STAGE_1"
    }
]
```

---

# 15. APIs Required

---

## Activate Strategy

```http
POST /strategy/activate
```

---

## Deactivate Strategy

```http
POST /strategy/deactivate
```

---

## Strategy Status

```http
GET /strategy/status
```

---

## Worker Health

```http
GET /worker/health
```

---

# 16. Frontend Requirements

Dashboard shall display:

```text
Worker Status

Active Strategies

Position Summary

Strategy Metrics

Quick Actions
```

---

# 17. Audit Requirements

The following actions shall be logged.

```text
Strategy Activated

Strategy Paused

Buy Executed

Sell Executed

Stop Loss Triggered

Strategy Completed
```

---

# 18. Future Enhancements

The system should support:

```text
Trailing Stop Loss

Backtesting Engine

Multiple Brokers

Paper Trading

Notifications

Telegram Alerts

Email Alerts

Multiple EMA Strategies

WebSocket Based Tick Processing
```

---

# 19. Acceptance Criteria

The strategy implementation shall be considered complete when:

```text
✓ Buy signals are generated correctly.

✓ Orders are placed only during configured time window.

✓ Average price calculation is accurate.

✓ Stage 1 sell executes correctly.

✓ Stage 2 sell executes correctly.

✓ Stage 3 sell executes correctly.

✓ Stop loss works.

✓ Risk limits are enforced.

✓ Worker executes every configured interval.

✓ Execution history is maintained.

✓ Dashboard reflects real-time strategy state.
```

---

# 20. Conclusion

SmartTradeBot EMA Strategy provides a disciplined rule-based approach to trading by combining:

• Trend-based entry using EMA.

• Controlled buying within predefined market windows.

• Weighted-average profit management.

• Multi-stage profit realization.

• Automated risk controls.

The strategy is designed to eliminate emotional decision-making and support scalable automated execution using Zerodha APIs.
