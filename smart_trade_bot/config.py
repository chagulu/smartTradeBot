import os


class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, "..", "smarttradebot.db")
    FLASK_SECRET_KEY = os.environ.get("SMARTTRADEBOT_SECRET_KEY", "change_this_secret")
    ZERODHA_API_KEY = os.environ.get("SMARTTRADEBOT_API_KEY", "")
    ZERODHA_API_SECRET = os.environ.get("SMARTTRADEBOT_API_SECRET", "")
    SCHEDULE_INTERVAL_SECONDS = int(os.environ.get("SMARTTRADEBOT_SCHEDULE_INTERVAL_SECONDS", "15"))
