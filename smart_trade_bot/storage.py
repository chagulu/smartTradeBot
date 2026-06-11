from smart_trade_bot.database import db
from smart_trade_bot.models import User

class Storage:
    def __init__(self, db_path):
        self.db_path = db_path

    def init_db(self):
        # Table creation is handled by Flask-Migrate, 
        # but we ensure structure here if needed.
        pass

    def get_access_token(self, user_id):
        """Retrieve access token from DB."""
        # For 'default', we just grab the first user for now
        user = User.query.first()
        if user:
            return user.access_token
        return None