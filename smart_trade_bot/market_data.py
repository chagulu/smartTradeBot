from kiteconnect import KiteConnect
from .config import Config


class KiteMarketDataProvider:
    def __init__(self, kite_client):
        self.kite = kite_client

    def get_ltp(self, instruments):
        if not instruments:
            return {}
        return self.kite.ltp(instruments)

    def get_historical(self, instrument_token, from_date, to_date, interval="15minute"):
        return self.kite.historical_data(instrument_token, from_date, to_date, interval)


class KiteClientFactory:
    @staticmethod
    def create(access_token=None):
        kite = KiteConnect(api_key=Config.ZERODHA_API_KEY)
        if access_token:
            kite.set_access_token(access_token)
        return kite
