from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta
from smart_trade_bot.config import Config

class KiteClientFactory:
    @staticmethod
    def create(access_token=None):
        kite = KiteConnect(api_key=Config.ZERODHA_API_KEY)
        if access_token:
            kite.set_access_token(access_token)
        return kite

class KiteMarketDataProvider:
    def __init__(self, kite_client):
        self.kite = kite_client

    def get_ltp(self, symbol):
        # Assumes NSE exchange for simplicity
        instrument = f"NSE:{symbol}"
        data = self.kite.ltp(instrument)
        return data[instrument]['last_price']

    def get_ema(self, symbol, period, interval='day'):
        instrument_token = self._get_instrument_token(symbol)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=period * 2) # Fetch extra data for accurate EMA
        
        records = self.kite.historical_data(instrument_token, from_date, to_date, interval)
        df = pd.DataFrame(records)
        if df.empty:
            return None
        
        ema_series = df['close'].ewm(span=period, adjust=False).mean()
        return ema_series.iloc[-1], df['close'].iloc[-1]

    def _get_instrument_token(self, symbol):
        # In a real app, cache this mapping from kite.instruments()
        instruments = self.kite.instruments("NSE")
        for inst in instruments:
            if inst['tradingsymbol'] == symbol:
                return inst['instrument_token']
        return None