import statistics
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify


class EMAConditionalStrategyEngine:
    def __init__(self, market_data, order_executor, storage):
        self.market_data = market_data
        self.order_executor = order_executor
        self.storage = storage

    def calculate_ema(self, prices, period=20):
        if len(prices) < period:
            return None
        sma = statistics.fmean(prices[-period:])
        multiplier = 2 / (period + 1)
        ema = sma
        for price in prices[-period + 1:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def evaluate_buy_condition(self, strategy):
        symbol = strategy["symbol"]
        period = strategy["ema_period"]
        history = self.market_data.get_historical(symbol, datetime.utcnow() - timedelta(days=5), datetime.utcnow(), "15minute")
        closes = [item["close"] for item in history if item.get("close") is not None]
        ema = self.calculate_ema(closes, period=period)
        if ema is None or not closes:
            return None

        ltp = self.market_data.get_ltp([symbol])
        current_price = self._extract_last_price(ltp, symbol)
        if current_price <= 0:
            return None

        if current_price > ema and closes[-1] > ema:
            return {
                "symbol": symbol,
                "entry_price": current_price,
                "quantity": strategy["quantity"],
                "strategy_id": strategy["id"],
            }
        return None

    def evaluate_sell_stages(self, position, strategy, current_price):
        targets = strategy["profit_targets"]
        stage = position["target_stage"]
        if stage >= len(targets):
            return None

        target_price = position["entry_price"] * (1 + targets[stage])
        if current_price >= target_price:
            return {
                "symbol": position["symbol"],
                "quantity": position["quantity"],
                "target_stage": stage + 1,
                "target_price": target_price,
            }
        return None

    def evaluate_active_strategies(self):
        active_strategies = self.storage.get_active_strategies()
        for strategy in active_strategies:
            buy_order = self.evaluate_buy_condition(strategy)
            if buy_order:
                order = self.order_executor.place_order(
                    symbol=buy_order["symbol"],
                    quantity=buy_order["quantity"],
                    transaction_type="BUY",
                )
                self.storage.save_position(
                    strategy_id=buy_order["strategy_id"],
                    symbol=buy_order["symbol"],
                    quantity=buy_order["quantity"],
                    entry_price=buy_order["entry_price"],
                )
                continue

        open_positions = self.storage.get_open_positions()
        for position in open_positions:
            ltp = self.market_data.get_ltp([position["symbol"]])
            current_price = self._extract_last_price(ltp, position["symbol"])
            if current_price <= 0:
                continue

            strategy = next((s for s in active_strategies if s["id"] == position["strategy_id"]), None)
            if not strategy:
                continue

            sell_order = self.evaluate_sell_stages(position, strategy, current_price)
            if sell_order:
                self.order_executor.place_order(
                    symbol=sell_order["symbol"],
                    quantity=sell_order["quantity"],
                    transaction_type="SELL",
                )
                self.storage.update_position(position["id"], target_stage=sell_order["target_stage"])
                if sell_order["target_stage"] >= len(strategy["profit_targets"]):
                    self.storage.update_position(position["id"], status="closed")

    @staticmethod
    def _extract_last_price(ltp_response, symbol):
        if isinstance(ltp_response, dict):
            symbol_data = ltp_response.get(symbol)
            if symbol_data and isinstance(symbol_data, dict):
                return float(symbol_data.get("last_price", 0) or 0)
        return 0


def create_strategy_blueprint(engine, storage):
    strategy_bp = Blueprint("strategy", __name__)

    @strategy_bp.route("/activate", methods=["POST"])
    def activate():
        payload = request.get_json(force=True)
        symbol = payload.get("symbol")
        ema_period = int(payload.get("ema_period", 20))
        quantity = int(payload.get("quantity", 1))
        entry_buffer_percent = float(payload.get("entry_buffer_percent", 0.0))
        profit_targets = payload.get("profit_targets", [0.02, 0.04])
        stop_loss = float(payload.get("stop_loss", 0.01))

        if not symbol:
            return jsonify({"error": "symbol is required"}), 400

        strategy_id = storage.save_strategy(
            symbol=symbol,
            ema_period=ema_period,
            quantity=quantity,
            entry_buffer_percent=entry_buffer_percent,
            profit_targets=profit_targets,
            stop_loss=stop_loss,
        )
        return jsonify({"message": "strategy_activated", "strategy_id": strategy_id})

    @strategy_bp.route("/deactivate", methods=["POST"])
    def deactivate():
        payload = request.get_json(force=True)
        strategy_id = payload.get("strategy_id")
        if strategy_id is None:
            return jsonify({"error": "strategy_id is required"}), 400
        storage.deactivate_strategy(strategy_id)
        return jsonify({"message": "strategy_deactivated", "strategy_id": strategy_id})

    @strategy_bp.route("/status", methods=["GET"])
    def status():
        active = storage.get_active_strategies()
        return jsonify({"active_strategies": active})

    return strategy_bp
