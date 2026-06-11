from flask import Blueprint, request, jsonify
from smart_trade_bot.models import User, db

def create_auth_blueprint(storage):
    bp = Blueprint("auth", __name__)

    @bp.route("/login", methods=["POST"])
    def login():
        data = request.json
        request_token = data.get("request_token")
        user_id = data.get("user_id")
        
        # In a real app, exchange request_token for access_token here
        # then save to DB
        user = User.query.filter_by(zerodha_user_id=user_id).first()
        if not user:
            user = User(zerodha_user_id=user_id)
            db.session.add(user)
        
        user.access_token = "mock_token" # Should be from Zerodha
        db.session.commit()
        
        return jsonify({"message": "login_successful", "user_id": user_id})

    return bp