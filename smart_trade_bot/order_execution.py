from kiteconnect import KiteConnect


class OrderExecutor:
    def __init__(self, kite_client):
        self.kite = kite_client

    def place_order(self, symbol, quantity, transaction_type, order_type="MARKET", product="MIS"):
        return self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=self._resolve_exchange(symbol),
            tradingsymbol=self._resolve_tradingsymbol(symbol),
            transaction_type=transaction_type,
            quantity=quantity,
            order_type=order_type,
            product=product,
        )

    def modify_order(self, order_id, quantity=None, price=None, order_type=None):
        kwargs = {"order_id": order_id}
        if quantity is not None:
            kwargs["quantity"] = quantity
        if price is not None:
            kwargs["price"] = price
        if order_type is not None:
            kwargs["order_type"] = order_type
        return self.kite.modify_order(**kwargs)

    def cancel_order(self, order_id):
        return self.kite.cancel_order(order_id)

    @staticmethod
    def _resolve_exchange(symbol):
        if symbol.startswith("NSE:") or symbol.startswith("BSE:"):
            return symbol.split(":")[0]
        return "NSE"

    @staticmethod
    def _resolve_tradingsymbol(symbol):
        return symbol.split(":")[-1]
