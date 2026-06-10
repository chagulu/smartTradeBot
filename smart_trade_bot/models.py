from datetime import datetime
from .database import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    zerodha_user_id = db.Column(db.String(50))
    zerodha_access_token = db.Column(db.String(255))
    zerodha_public_token = db.Column(db.String(255))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuthToken(db.Model):
    __tablename__ = "auth_tokens"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    token_type = db.Column(db.String(50))
    expires_at = db.Column(db.DateTime)
    is_revoked = db.Column(db.Boolean, default=False)
    device_info = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Portfolio(db.Model):
    __tablename__ = "portfolios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    total_value = db.Column(db.Float, default=0.0)
    cash_balance = db.Column(db.Float, default=0.0)
    invested_value = db.Column(db.Float, default=0.0)
    unrealized_pnl = db.Column(db.Float, default=0.0)
    realized_pnl = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Holding(db.Model):
    __tablename__ = "holdings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    instrument_token = db.Column(db.String(50))
    tradingsymbol = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    average_price = db.Column(db.Float, default=0.0)
    current_price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'))
    order_id = db.Column(db.String(100), unique=True)
    tradingsymbol = db.Column(db.String(50), nullable=False)
    exchange = db.Column(db.String(20))
    transaction_type = db.Column(db.String(20)) # BUY, SELL
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    order_type = db.Column(db.String(20)) # MARKET, LIMIT
    status = db.Column(db.String(50))
    filled_quantity = db.Column(db.Integer, default=0)
    average_price = db.Column(db.Float, default=0.0)
    trigger_price = db.Column(db.Float)
    variety = db.Column(db.String(20))
    product = db.Column(db.String(20))
    order_meta = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.String(50))
    changes = db.Column(db.Text) # JSON string
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmaStrategy(db.Model):
    __tablename__ = "ema_strategies"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    symbol = db.Column(db.String(50), nullable=False)
    ema_period = db.Column(db.Integer, default=100)
    buy_time_start = db.Column(db.String(5))
    buy_time_end = db.Column(db.String(5))
    stage_1_profit_percent = db.Column(db.Float)
    stage_2_profit_percent = db.Column(db.Float)
    stage_3_profit_percent = db.Column(db.Float)
    stop_loss_percent = db.Column(db.Float)
    max_position_size = db.Column(db.Integer)
    max_capital_allocation = db.Column(db.Float)
    max_daily_loss = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50))
    current_position_quantity = db.Column(db.Integer, default=0)
    current_position_avg_price = db.Column(db.Float, default=0.0)
    execution_history = db.Column(db.Text) # JSON string
    total_buy_orders = db.Column(db.Integer, default=0)
    total_sell_orders = db.Column(db.Integer, default=0)
    total_pnl = db.Column(db.Float, default=0.0)
    last_activity_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionLog(db.Model):
    __tablename__ = "execution_logs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('ema_strategies.id'), nullable=False)
    action = db.Column(db.String(20)) # BUY / SELL
    symbol = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    broker_order_id = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ConditionalOrder(db.Model):
    __tablename__ = "conditional_orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(255))
    trigger_price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    transaction_type = db.Column(db.String(20))
    status = db.Column(db.String(50))
    retry_count = db.Column(db.Integer, default=0)
    executed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StrategyBacktest(db.Model):
    __tablename__ = "strategy_backtests"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('ema_strategies.id'), nullable=False)
    symbol = db.Column(db.String(50))
    from_date = db.Column(db.DateTime)
    to_date = db.Column(db.DateTime)
    initial_capital = db.Column(db.Float)
    final_capital = db.Column(db.Float)
    total_return = db.Column(db.Float)
    win_rate = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)