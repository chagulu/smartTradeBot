from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from smart_trade_bot.config import Config
from smart_trade_bot.database import db
from smart_trade_bot.storage import Storage
from smart_trade_bot.auth import create_auth_blueprint
from smart_trade_bot.strategy_engine import (
    create_strategy_blueprint,
    EMAConditionalStrategyEngine
)
from smart_trade_bot.market_data import (
    KiteMarketDataProvider,
    KiteClientFactory
)
from smart_trade_bot.order_execution import OrderExecutor
from smart_trade_bot.worker import WorkerEngine


def create_app():
    app = Flask(__name__)

    # Flask Configuration
    app.config["SECRET_KEY"] = Config.FLASK_SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
        Config.SQLALCHEMY_TRACK_MODIFICATIONS
    )

    # Enable CORS for React Frontend
    CORS(
        app,
        origins=["http://localhost:5173"],
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # Initialize Database and Migrations
    db.init_app(app)

    import smart_trade_bot.models  # Required for Alembic

    migrate = Migrate(app, db)

    # Initialize Storage
    storage = Storage(Config.DATABASE_PATH)
    storage.init_db()

    # Initialize Zerodha Components
    access_token = storage.get_access_token("default")

    kite = KiteClientFactory.create(
        access_token=access_token
    )

    market_data = KiteMarketDataProvider(kite)

    order_executor = OrderExecutor(kite)

    # Initialize Strategy Engine
    engine = EMAConditionalStrategyEngine(
        market_data,
        order_executor,
        storage
    )

    # Background Worker
    worker = WorkerEngine(
        engine,
        interval_seconds=Config.SCHEDULE_INTERVAL_SECONDS
    )

    # Register Blueprints
    app.register_blueprint(
        create_auth_blueprint(storage),
        url_prefix="/auth"
    )

    app.register_blueprint(
        create_strategy_blueprint(engine, storage),
        url_prefix="/strategy"
    )

    # Health Endpoint
    @app.route("/worker/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "interval_seconds": Config.SCHEDULE_INTERVAL_SECONDS
        })

    # Start Worker
    worker.start()

    return app


if __name__ == "__main__":
    application = create_app()

    application.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )