from kiteconnect import KiteConnect

class OrderExecutor:
    def __init__(self, kite):
        self.kite = kite

    def place_order(self, symbol, action, quantity, order_type="MARKET"):
        """Place an order via Kite Connect."""
        try:
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=self.kite.EXCHANGE_NSE,
                tradingsymbol=symbol,
                transaction_type=action.upper(),
                quantity=quantity,
                product=self.kite.PRODUCT_CNC,
                order_type=order_type
            )
            return order_id
        except Exception as e:
            print(f"Order placement failed: {e}")
            return None