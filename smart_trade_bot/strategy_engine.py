from datetime import datetime
from flask import Blueprint, request, jsonify

from smart_trade_bot.models import (
    ConditionalOrder,
    EmaStrategy,
    Execution,
    Position,
    db,
)


DEFAULT_PROFIT_TARGETS = (0.10, 0.20, 0.30)
DEFAULT_STOP_LOSS_PERCENT = 0.15
VALID_CONDITIONS = {"PRICE_ABOVE", "PRICE_BELOW", "EMA_ABOVE", "EMA_BELOW"}
VALID_ACTIONS = {"BUY", "SELL"}


class EMAConditionalStrategyEngine:
    def __init__(self, market_data, order_executor, storage):
        self.market_data = market_data
        self.order_executor = order_executor
        self.storage = storage

    def run_cycle(self):
        """Main evaluation loop called by the worker."""
        # 1. Evaluate standalone conditional orders
        conditional_orders = ConditionalOrder.query.filter_by(status="WAITING").all()
        for order in conditional_orders:
            self._evaluate_conditional_order(order)

        # 2. Evaluate EMA Strategies
        strategies = EmaStrategy.query.filter_by(status="ACTIVE").all()
        for strategy in strategies:
            self._evaluate_strategy(strategy)

        # 3. Check Positions for Profit Booking / Stop Loss
        positions = Position.query.filter(Position.quantity > 0).all()
        for pos in positions:
            self._manage_exit_strategy(pos)

    def _evaluate_conditional_order(self, order):
        if not self._condition_matches(order):
            return

        order.status = "TRIGGERED"
        db.session.commit()

        order_id = self.order_executor.place_order(
            order.symbol,
            order.action,
            order.quantity,
        )

        if not order_id:
            order.status = "FAILED"
            db.session.commit()
            return

        price = self.market_data.get_ltp(order.symbol) or order.trigger_price or 0
        self._record_execution(
            order_id=order.id,
            symbol=order.symbol,
            action=order.action,
            quantity=order.quantity,
            price=price,
            kite_order_id=order_id,
        )

        if order.action == "BUY":
            self._update_position_after_buy(order, price, order_id)
        else:
            self._update_position_after_sell(order.user_id, order.symbol, order.quantity)

        order.status = "EXECUTED"
        order.executed_at = datetime.utcnow()
        db.session.commit()

    def _condition_matches(self, order):
        condition = order.condition_type.upper()
        if condition not in VALID_CONDITIONS:
            order.status = "FAILED"
            db.session.commit()
            return False

        ltp = self.market_data.get_ltp(order.symbol)
        if ltp is None:
            return False

        if condition == "PRICE_ABOVE":
            return order.trigger_price is not None and ltp > order.trigger_price
        if condition == "PRICE_BELOW":
            return order.trigger_price is not None and ltp < order.trigger_price

        ema_period = order.ema_period or 100
        ema = self.market_data.get_ema(order.symbol, ema_period)
        if ema is None:
            return False

        if condition == "EMA_ABOVE":
            return ltp > ema
        return ltp < ema

    def _evaluate_strategy(self, strategy):
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        
        # EMA Entry Logic (Section 10)
        if strategy.buy_time_start <= current_time_str <= strategy.buy_time_end:
            ltp = self.market_data.get_ltp(strategy.symbol)
            ema = self.market_data.get_ema(strategy.symbol, strategy.ema_period)
            
            if ltp and ema and ltp < ema:
                print(f"EMA Entry Triggered for {strategy.symbol}: Price {ltp} < EMA {ema}")
                order_id = self.order_executor.place_order(strategy.symbol, "BUY", strategy.quantity)
                if order_id:
                    self._update_position_after_buy(strategy, ltp, order_id)
                    self._record_execution(
                        order_id=strategy.id,
                        symbol=strategy.symbol,
                        action="BUY",
                        quantity=strategy.quantity,
                        price=ltp,
                        kite_order_id=order_id,
                    )
                    db.session.commit()

    def _manage_exit_strategy(self, pos):
        ltp = self.market_data.get_ltp(pos.symbol)
        if not ltp:
            return

        # Stop Loss Logic (Section 14)
        sl_price = pos.average_price * (1 - DEFAULT_STOP_LOSS_PERCENT)
        if ltp <= sl_price:
            print(f"STOP LOSS HIT for {pos.symbol}")
            order_id = self.order_executor.place_order(pos.symbol, "SELL", pos.quantity)
            if order_id:
                quantity = pos.quantity
                self._record_execution(
                    order_id=pos.id,
                    symbol=pos.symbol,
                    action="SELL",
                    quantity=quantity,
                    price=ltp,
                    stage=0,
                    kite_order_id=order_id,
                )
                self._update_position_after_sell(pos.user_id, pos.symbol, quantity)
                db.session.commit()
            return

        executed_stages = {
            row.stage
            for row in Execution.query.filter_by(
                order_id=pos.id,
                symbol=pos.symbol,
                action="SELL",
            ).all()
            if row.stage
        }

        for stage, target in enumerate(DEFAULT_PROFIT_TARGETS, start=1):
            if stage in executed_stages:
                continue

            target_price = pos.average_price * (1 + target)
            if ltp < target_price:
                continue

            quantity = pos.quantity if stage == 3 else max(1, pos.quantity // 2)
            order_id = self.order_executor.place_order(pos.symbol, "SELL", quantity)
            if not order_id:
                return

            self._record_execution(
                order_id=pos.id,
                symbol=pos.symbol,
                action="SELL",
                quantity=quantity,
                price=ltp,
                stage=stage,
                kite_order_id=order_id,
            )
            self._update_position_after_sell(pos.user_id, pos.symbol, quantity)
            db.session.commit()
            return

    def _update_position_after_buy(self, strategy, price, kite_id):
        user_id = getattr(strategy, "user_id", 1)
        symbol = strategy.symbol
        quantity = strategy.quantity

        position = Position.query.filter_by(user_id=user_id, symbol=symbol).first()
        if not position:
            position = Position(user_id=user_id, symbol=symbol, quantity=0)
            db.session.add(position)

        current_quantity = position.quantity or 0
        current_invested = position.invested_amount or 0
        buy_value = price * quantity
        new_quantity = current_quantity + quantity
        new_invested = current_invested + buy_value

        position.quantity = new_quantity
        position.invested_amount = new_invested
        position.average_price = new_invested / new_quantity if new_quantity else 0
        position.current_pnl = 0

    def _update_position_after_sell(self, user_id, symbol, quantity):
        position = Position.query.filter_by(user_id=user_id, symbol=symbol).first()
        if not position:
            return

        sell_quantity = min(quantity, position.quantity or 0)
        remaining_quantity = (position.quantity or 0) - sell_quantity
        position.quantity = remaining_quantity
        position.invested_amount = position.average_price * remaining_quantity
        if remaining_quantity == 0:
            position.average_price = 0
            position.current_pnl = 0

    def _record_execution(
        self,
        order_id,
        symbol,
        action,
        quantity,
        price,
        kite_order_id,
        stage=None,
    ):
        execution = Execution(
            order_id=order_id,
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            stage=stage,
            kite_order_id=kite_order_id,
        )
        db.session.add(execution)

def create_strategy_blueprint(engine, storage):
    bp = Blueprint("strategy", __name__)

    @bp.route("/status", methods=["GET"])
    def status():
        active = EmaStrategy.query.filter_by(status="ACTIVE").all()
        return jsonify({
            "active_strategies": [{
                "id": s.id,
                "symbol": s.symbol,
                "ema_period": s.ema_period,
                "quantity": s.quantity,
                "profit_targets": [
                    s.stage_1_profit_percent,
                    s.stage_2_profit_percent,
                    s.stage_3_profit_percent,
                ],
                "stop_loss": s.stop_loss_percent,
                "status": s.status,
            } for s in active]
        })

    @bp.route("/activate", methods=["POST"])
    def activate():
        data = request.json
        new_strat = EmaStrategy(
            user_id=1, # Mocked for now
            symbol=data['symbol'].upper(),
            ema_period=data.get('ema_period', 100),
            quantity=data.get('quantity', 1),
            stage_1_profit_percent=data.get("stage_1_profit_percent", 0.10),
            stage_2_profit_percent=data.get("stage_2_profit_percent", 0.20),
            stage_3_profit_percent=data.get("stage_3_profit_percent", 0.30),
            stop_loss_percent=data.get("stop_loss_percent", 0.15),
        )
        db.session.add(new_strat)
        db.session.commit()
        return jsonify({"message": "strategy_activated", "strategy_id": new_strat.id})

    @bp.route("/deactivate", methods=["POST"])
    def deactivate():
        data = request.get_json() or {}
        strategy = EmaStrategy.query.get(data.get("strategy_id"))
        if not strategy:
            return jsonify({"error": "strategy_not_found"}), 404

        strategy.status = "INACTIVE"
        db.session.commit()
        return jsonify({
            "message": "strategy_deactivated",
            "strategy_id": strategy.id,
        })

    return bp
