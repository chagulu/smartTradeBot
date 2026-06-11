from kiteconnect import KiteConnect
from smart_trade_bot.config import Config
import pandas as pd

class KiteClientFactory:
    @staticmethod
    def create(access_token=None):
        kite = KiteConnect(api_key=Config.ZERODHA_API_KEY)
        if access_token:
            kite.set_access_token(access_token)
        return kite

class KiteMarketDataProvider:
    def __init__(self, kite):
        self.kite = kite

    def get_ltp(self, symbol):
        """Fetch Last Traded Price."""
        try:
            data = self.kite.ltp(f"NSE:{symbol}")
            return data.get(f"NSE:{symbol}", {}).get("last_price")
        except Exception:
            return None

    def get_ema(self, symbol, period, interval="day"):
        """Calculate EMA using historical data."""
        try:
            # Fetch enough data to calculate EMA (e.g., 2x period)
            to_date = pd.Timestamp.now()
            from_date = to_date - pd.Timedelta(days=period * 2)
            
            # Note: You'd need the instrument_token for historical data in production
            # Here we assume a mapping or use kite.instruments() to find it
            # For demonstration, using a placeholder logic
            instrument_token = 256265 # Example for INFY
            
            records = self.kite.historical_data(
                instrument_token, 
                from_date.strftime("%Y-%m-%d"), 
                to_date.strftime("%Y-%m-%d"), 
                interval
            )
            
            df = pd.DataFrame(records)
            if df.empty:
                return None
            
            return df['close'].ewm(span=period, adjust=False).mean().iloc[-1]
        except Exception:
            return None