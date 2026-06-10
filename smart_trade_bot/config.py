import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, "..", "smarttradebot.db")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "Test@123")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_NAME = os.environ.get("DB_NAME", "smarttradebot")
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_SECRET_KEY = os.environ.get("SMARTTRADEBOT_SECRET_KEY", "change_this_secret")
    ZERODHA_API_KEY = os.environ.get("SMARTTRADEBOT_API_KEY", "nx0mi6cqth8lm0cz")
    ZERODHA_API_SECRET = os.environ.get("SMARTTRADEBOT_API_SECRET", "a4ola4mkpazvkjzb380ruy8si8zctgg2")
    ZERODHA_CLIENT_ID = os.environ.get("SMARTTRADEBOT_CLIENT_ID", "UPP323")
    ZERODHA_REDIRECT_URL = os.environ.get("SMARTTRADEBOT_REDIRECT_URL", "http://localhost:5001/callback")
    SCHEDULE_INTERVAL_SECONDS = int(os.environ.get("SMARTTRADEBOT_SCHEDULE_INTERVAL_SECONDS", "15"))
