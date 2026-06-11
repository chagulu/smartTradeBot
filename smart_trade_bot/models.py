from datetime import datetime
from smart_trade_bot.database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    zerodha_user_id = db.Column(db.String(50), unique=True)
    zerodha_access_token = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EMAStrategy(db.Model):
    __tablename__ = 'ema_strategies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    ema_period = db.Column(db.Integer, default=100)
    
    # Buy Window
    buy_time_start = db.Column(db.String(5), default="15:15")
    buy_time_end = db.Column(db.String(5), default="15:30")
    
    # Sell Config (Percentages as floats, e.g., 0.10 for 10%)
    stage_1_profit_percent = db.Column(db.Float, default=0.10)
    stage_2_profit_percent = db.Column(db.Float, default=0.20)
    stage_3_profit_percent = db.Column(db.Float, default=0.30)
    stop_loss_percent = db.Column(db.Float, default=0.15)
    
    # Risk Controls
    max_position_size = db.Column(db.Integer, default=1000)
    max_capital_allocation = db.Column(db.Float, default=50000.0)
    max_daily_loss = db.Column(db.Float, default=5000.0)
    
    # Execution State
    current_position_quantity = db.Column(db.Integer, default=0)
    current_position_avg_price = db.Column(db.Float, default=0.0)
    
    # Stage Tracking
    stage_1_completed = db.Column(db.Boolean, default=False)
    stage_2_completed = db.Column(db.Boolean, default=False)
    stage_3_completed = db.Column(db.Boolean, default=False)
    
    status = db.Column(db.String(20), default="ACTIVE") # ACTIVE, PAUSED, STOPPED, COMPLETED
    is_active = db.Column(db.Boolean, default=True)
    
    total_buy_orders = db.Column(db.Integer, default=0)
    total_sell_orders = db.Column(db.Integer, default=0)
    total_pnl = db.Column(db.Float, default=0.0)
    
    last_activity_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionLog(db.Model):
    __tablename__ = 'execution_logs'
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('ema_strategies.id'))
    action = db.Column(db.String(10)) # BUY / SELL
    symbol = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    broker_order_id = db.Column(db.String(100))
    remarks = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)