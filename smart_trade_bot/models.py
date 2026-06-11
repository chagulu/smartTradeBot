from datetime import datetime
from smart_trade_bot.database import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    zerodha_user_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    access_token = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConditionalOrder(db.Model):
    __tablename__ = "conditional_orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # BUY or SELL
    condition_type = db.Column(db.String(50), nullable=False) # PRICE_ABOVE, PRICE_BELOW, etc.
    trigger_price = db.Column(db.Float)
    ema_period = db.Column(db.Integer)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="WAITING") # WAITING, TRIGGERED, EXECUTED, FAILED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)

class Position(db.Model):
    __tablename__ = "positions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    average_price = db.Column(db.Float, default=0.0)
    invested_amount = db.Column(db.Float, default=0.0)
    current_pnl = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Execution(db.Model):
    __tablename__ = "executions"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer) # Reference to internal ID or Strategy ID
    symbol = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stage = db.Column(db.Integer) # 1, 2, or 3 for profit booking
    kite_order_id = db.Column(db.String(100))
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)

class EmaStrategy(db.Model):
    __tablename__ = "ema_strategies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    ema_period = db.Column(db.Integer, default=100)
    quantity = db.Column(db.Integer, nullable=False)
    buy_time_start = db.Column(db.String(10), default="15:15")
    buy_time_end = db.Column(db.String(10), default="15:30")
    stage_1_profit_percent = db.Column(db.Float, default=0.10)
    stage_2_profit_percent = db.Column(db.Float, default=0.20)
    stage_3_profit_percent = db.Column(db.Float, default=0.30)
    stop_loss_percent = db.Column(db.Float, default=0.15)
    status = db.Column(db.String(20), default="ACTIVE")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)