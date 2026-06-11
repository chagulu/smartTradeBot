from datetime import datetime
from flask import Blueprint, request, jsonify
from smart_trade_bot.models import EMAStrategy, ExecutionLog, db
import math

class EMAConditionalStrategyEngine:
    def __init__(self, market_data, order_executor, storage):
        self.market_data = market_data
        self.executor = order_executor
        self.storage = storage

    def run_all(self):
        active_strategies = EMAStrategy.query.filter_by(is_active=True, status="ACTIVE").all()
        for strategy in active_strategies:
            self.process_strategy(strategy)

    def process_strategy(self, strategy):
        try:
            current_price = self.market_data.get_ltp(strategy.symbol)
            now = datetime.now()
            
            # 1. Evaluate Buy Condition
            self.evaluate_buy(strategy, current_price, now)
            
            # 2. Evaluate Sell/Exit Conditions (only if position exists)
            if strategy.current_position_quantity > 0:
                self.evaluate_exit(strategy, current_price)
                
        except Exception as e:
            print(f"Error processing {strategy.symbol}: {e}")

    def evaluate_buy(self, strategy, current_price, now):
        # Condition: Time Window
        start_time = datetime.strptime(strategy.buy_time_start, "%H:%M").time()
        end_time = datetime.strptime(strategy.buy_time_end, "%H:%M").time()
        
        if not (start_time <= now.time() <= end_time):
            return

        # Condition: EMA Logic (Daily candle close below EMA)
        ema_val, last_close = self.market_data.get_ema(strategy.symbol, strategy.ema_period)
        if last_close < ema_val:
            # Risk limit check
            if strategy.current_position_quantity >= strategy.max_position_size:
                return
                
            # Calculate quantity to buy (This example buys 10% of max per signal)
            qty_to_buy = 10 # Example fixed increment
            
            order_id = self.executor.place_buy_order(strategy.symbol, qty_to_buy)
            self.update_position_after_buy(strategy, qty_to_buy, current_price, order_id)

    def update_position_after_buy(self, strategy, qty, price, order_id):
        old_total = strategy.current_position_quantity * strategy.current_position_avg_price
        new_qty = strategy.current_position_quantity + qty
        new_avg = (old_total + (qty * price)) / new_qty
        
        strategy.current_position_quantity = new_qty
        strategy.current_position_avg_price = new_avg
        strategy.total_buy_orders += 1
        strategy.last_activity_at = datetime.utcnow()
        
        log = ExecutionLog(strategy_id=strategy.id, action="BUY", symbol=strategy.symbol, 
                           quantity=qty, price=price, broker_order_id=order_id)
        db.session.add(log)
        db.session.commit()

    def evaluate_exit(self, strategy, current_price):
        avg = strategy.current_position_avg_price
        qty = strategy.current_position_quantity

        # Stop Loss
        if current_price <= avg * (1 - strategy.stop_loss_percent):
            self.execute_sell(strategy, qty, current_price, "STOP_LOSS")
            strategy.status = "PAUSED" # Pause strategy after SL as per spec
            return

        # Stage 3: Avg + 30% (Sell Remaining)
        if not strategy.stage_3_completed and current_price >= avg * (1 + strategy.stage_3_profit_percent):
            self.execute_sell(strategy, qty, current_price, "STAGE_3")
            strategy.stage_3_completed = True
            strategy.status = "COMPLETED"
            return

        # Stage 2: Avg + 20% (Sell 50% of remaining)
        if not strategy.stage_2_completed and current_price >= avg * (1 + strategy.stage_2_profit_percent):
            sell_qty = math.floor(qty * 0.5)
            self.execute_sell(strategy, sell_qty, current_price, "STAGE_2")
            strategy.stage_2_completed = True
            return

        # Stage 1: Avg + 10% (Sell 50% of total)
        if not strategy.stage_1_completed and current_price >= avg * (1 + strategy.stage_1_profit_percent):
            sell_qty = math.floor(qty * 0.5)
            self.execute_sell(strategy, sell_qty, current_price, "STAGE_1")
            strategy.stage_1_completed = True
            return

    def execute_sell(self, strategy, qty, price, remarks):
        order_id = self.executor.place_sell_order(strategy.symbol, qty)
        strategy.current_position_quantity -= qty
        strategy.total_sell_orders += 1
        
        if strategy.current_position_quantity == 0:
            strategy.current_position_avg_price = 0
            
        log = ExecutionLog(strategy_id=strategy.id, action="SELL", symbol=strategy.symbol, 
                           quantity=qty, price=price, broker_order_id=order_id, remarks=remarks)
        db.session.add(log)
        db.session.commit()

def create_strategy_blueprint(engine, storage):
    bp = Blueprint("strategy", __name__)

    @bp.route("/activate", methods=["POST"])
    def activate():
        data = request.json
        strat = EMAStrategy(
            user_id=1, # Hardcoded for default user
            symbol=data['symbol'],
            ema_period=data.get('ema_period', 100),
            status="ACTIVE",
            is_active=True
        )
        db.session.add(strat)
        db.session.commit()
        return jsonify({"message": "strategy_activated", "strategy_id": strat.id})

    @bp.route("/deactivate", methods=["POST"])
    def deactivate():
        strat_id = request.json.get("strategy_id")
        strat = EMAStrategy.query.get(strat_id)
        if strat:
            strat.is_active = False
            strat.status = "STOPPED"
            db.session.commit()
        return jsonify({"message": "strategy_deactivated", "strategy_id": strat_id})

    @bp.route("/status", methods=["GET"])
    def status():
        strats = EMAStrategy.query.filter_by(is_active=True).all()
        output = []
        for s in strats:
            output.append({
                "id": s.id,
                "symbol": s.symbol,
                "ema_period": s.ema_period,
                "quantity": s.current_position_quantity,
                "avg_price": s.current_position_avg_price,
                "status": s.status,
                "stages": [s.stage_1_completed, s.stage_2_completed, s.stage_3_completed]
            })
        return jsonify({"active_strategies": output})

    return bp