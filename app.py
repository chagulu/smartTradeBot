from flask import Flask, jsonify
from flask_migrate import Migrate

from smart_trade_bot.config import Config
from smart_trade_bot.database import db
from smart_trade_bot.storage import Storage
from smart_trade_bot.auth import create_auth_blueprint
from smart_trade_bot.strategy_engine import create_strategy_blueprint, EMAConditionalStrategyEngine
from smart_trade_bot.market_data import KiteMarketDataProvider, KiteClientFactory
from smart_trade_bot.order_execution import OrderExecutor
from smart_trade_bot.worker import WorkerEngine


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.FLASK_SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

    # Initialize Database and Migrations
    db.init_app(app)
    import smart_trade_bot.models  # Required for Alembic to detect the schema
    migrate = Migrate(app, db)

    storage = Storage(Config.DATABASE_PATH)
    storage.init_db()

    access_token = storage.get_access_token("default")
    kite = KiteClientFactory.create(access_token=access_token)
    market_data = KiteMarketDataProvider(kite)
    order_executor = OrderExecutor(kite)
    engine = EMAConditionalStrategyEngine(market_data, order_executor, storage)
    worker = WorkerEngine(engine, interval_seconds=Config.SCHEDULE_INTERVAL_SECONDS)

    app.register_blueprint(create_auth_blueprint(storage), url_prefix="/auth")
    app.register_blueprint(create_strategy_blueprint(engine, storage), url_prefix="/strategy")

    @app.route("/worker/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "interval_seconds": Config.SCHEDULE_INTERVAL_SECONDS})

    worker.start()
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5001, debug=True)
