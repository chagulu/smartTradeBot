from flask import Blueprint, jsonify, request

from smart_trade_bot.models import ConditionalOrder, Execution, Position, User, db
from smart_trade_bot.strategy_engine import VALID_ACTIONS, VALID_CONDITIONS


OPEN_ORDER_STATUSES = {"OPEN", "TRIGGER PENDING", "VALIDATION PENDING"}


def create_api_blueprint(engine, market_data, order_executor, worker=None):
    bp = Blueprint("api", __name__)

    def get_or_create_default_user():
        user = User.query.first()
        if user:
            return user

        user = User(zerodha_user_id="default", email="default@smarttradebot.local")
        db.session.add(user)
        db.session.commit()
        return user

    def serialize_conditional_order(order):
        return {
            "id": order.id,
            "user_id": order.user_id,
            "symbol": order.symbol,
            "action": order.action,
            "condition_type": order.condition_type,
            "trigger_price": order.trigger_price,
            "ema_period": order.ema_period,
            "quantity": order.quantity,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "executed_at": (
                order.executed_at.isoformat() if order.executed_at else None
            ),
        }

    def serialize_position(position):
        ltp = market_data.get_ltp(position.symbol)
        current_value = (ltp or position.average_price or 0) * position.quantity
        invested_amount = position.invested_amount or 0
        return {
            "id": position.id,
            "user_id": position.user_id,
            "symbol": position.symbol,
            "quantity": position.quantity,
            "average_price": position.average_price,
            "invested_amount": invested_amount,
            "current_price": ltp,
            "current_value": current_value,
            "current_pnl": current_value - invested_amount,
        }

    def place_and_record_order(user_id, symbol, action, quantity):
        kite_order_id = order_executor.place_order(symbol, action, quantity)
        if not kite_order_id:
            return None

        price = market_data.get_ltp(symbol) or 0
        engine._record_execution(
            order_id=None,
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            kite_order_id=kite_order_id,
        )
        if action == "BUY":
            order_like = type(
                "ManualOrder",
                (),
                {"user_id": user_id, "symbol": symbol, "quantity": quantity},
            )()
            engine._update_position_after_buy(order_like, price, kite_order_id)
        else:
            engine._update_position_after_sell(user_id, symbol, quantity)

        db.session.commit()
        return {"kite_order_id": kite_order_id, "price": price}

    @bp.route("/dashboard", methods=["GET"])
    def dashboard():
        user = get_or_create_default_user()
        positions = Position.query.filter_by(user_id=user.id).all()
        position_payload = [serialize_position(position) for position in positions]
        total_investment = sum(item["invested_amount"] for item in position_payload)
        todays_pnl = sum(item["current_pnl"] for item in position_payload)

        return jsonify({
            "worker": worker.status() if worker else {"running": False},
            "portfolio": {
                "holdings": len(position_payload),
                "positions": position_payload,
                "todays_pnl": todays_pnl,
                "total_investment": total_investment,
            },
            "live_orders": fetch_live_orders(),
            "user": {
                "id": user.id,
                "email": user.email,
                "zerodha_client_id": user.zerodha_user_id,
            },
        })

    @bp.route("/portfolio", methods=["GET"])
    def portfolio():
        user = get_or_create_default_user()
        positions = Position.query.filter_by(user_id=user.id).all()
        payload = [serialize_position(position) for position in positions]
        return jsonify({
            "positions": payload,
            "total_investment": sum(item["invested_amount"] for item in payload),
            "current_value": sum(item["current_value"] for item in payload),
            "current_pnl": sum(item["current_pnl"] for item in payload),
        })

    @bp.route("/orders/live", methods=["GET"])
    def live_orders():
        return jsonify({"orders": fetch_live_orders()})

    def fetch_live_orders():
        try:
            orders = order_executor.kite.orders()
        except Exception:
            return []

        return [
            {
                "symbol": order.get("tradingsymbol"),
                "type": order.get("transaction_type"),
                "quantity": order.get("quantity"),
                "status": order.get("status"),
                "price": order.get("price") or order.get("average_price"),
            }
            for order in orders
            if order.get("status") in OPEN_ORDER_STATUSES
        ]

    @bp.route("/orders/place", methods=["POST"])
    def place_order():
        data = request.get_json() or {}
        user = get_or_create_default_user()
        symbol = str(data.get("symbol", "")).upper().strip()
        action = str(data.get("action", "")).upper().strip()
        quantity = data.get("quantity")

        if not symbol or action not in VALID_ACTIONS:
            return jsonify({"error": "symbol_and_valid_action_required"}), 400
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "positive_integer_quantity_required"}), 400

        result = place_and_record_order(user.id, symbol, action, quantity)
        if not result:
            return jsonify({"error": "order_placement_failed"}), 502

        return jsonify({
            "message": "order_placed",
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            **result,
        })

    @bp.route("/conditional-orders", methods=["POST"])
    def create_conditional_order():
        data = request.get_json() or {}
        user = get_or_create_default_user()
        symbol = str(data.get("symbol", "")).upper().strip()
        action = str(data.get("action", "")).upper().strip()
        condition_type = str(data.get("condition_type", "")).upper().strip()
        quantity = data.get("quantity")

        if not symbol or action not in VALID_ACTIONS:
            return jsonify({"error": "symbol_and_valid_action_required"}), 400
        if condition_type not in VALID_CONDITIONS:
            return jsonify({"error": "valid_condition_type_required"}), 400
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "positive_integer_quantity_required"}), 400

        if condition_type.startswith("PRICE") and data.get("trigger_price") is None:
            return jsonify({"error": "trigger_price_required"}), 400

        order = ConditionalOrder(
            user_id=user.id,
            symbol=symbol,
            action=action,
            condition_type=condition_type,
            trigger_price=data.get("trigger_price"),
            ema_period=data.get("ema_period"),
            quantity=quantity,
            status="WAITING",
        )
        db.session.add(order)
        db.session.commit()
        return jsonify(serialize_conditional_order(order)), 201

    @bp.route("/conditional-orders", methods=["GET"])
    def list_conditional_orders():
        orders = ConditionalOrder.query.order_by(ConditionalOrder.created_at.desc()).all()
        return jsonify({
            "conditional_orders": [
                serialize_conditional_order(order) for order in orders
            ],
        })

    @bp.route("/conditional-orders/<int:order_id>", methods=["DELETE"])
    def cancel_conditional_order(order_id):
        order = ConditionalOrder.query.get(order_id)
        if not order:
            return jsonify({"error": "conditional_order_not_found"}), 404
        if order.status in {"EXECUTED", "FAILED"}:
            return jsonify({"error": "conditional_order_already_final"}), 409

        order.status = "CANCELLED"
        db.session.commit()
        return jsonify(serialize_conditional_order(order))

    @bp.route("/executions", methods=["GET"])
    def executions():
        rows = Execution.query.order_by(Execution.executed_at.desc()).limit(100).all()
        return jsonify({
            "executions": [
                {
                    "id": row.id,
                    "order_id": row.order_id,
                    "symbol": row.symbol,
                    "action": row.action,
                    "quantity": row.quantity,
                    "price": row.price,
                    "stage": row.stage,
                    "kite_order_id": row.kite_order_id,
                    "executed_at": (
                        row.executed_at.isoformat() if row.executed_at else None
                    ),
                }
                for row in rows
            ],
        })

    return bp
