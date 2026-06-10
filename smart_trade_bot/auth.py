from flask import Blueprint, request, jsonify, session
from kiteconnect import KiteConnect
from .config import Config


def create_auth_blueprint(storage):
    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/login", methods=["POST"])
    def login():
        payload = request.get_json(force=True)
        request_token = payload.get("request_token")
        user_id = payload.get("user_id", "default")

        if not request_token:
            return jsonify({"error": "request_token is required"}), 400

        kite = KiteConnect(api_key=Config.ZERODHA_API_KEY)
        try:
            session_data = kite.generate_session(request_token, Config.ZERODHA_API_SECRET)
        except Exception as exc:
            return jsonify({"error": "authentication_failed", "details": str(exc)}), 502

        access_token = session_data.get("access_token")
        if not access_token:
            return jsonify({"error": "missing_access_token"}), 500

        storage.save_access_token(user_id, access_token)
        session["user_id"] = user_id

        return jsonify({
            "message": "login_successful",
            "user_id": user_id,
            "access_token": access_token,
            "session_data": session_data,
        })

    return auth_bp
