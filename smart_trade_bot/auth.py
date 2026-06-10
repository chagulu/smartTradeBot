from flask import Blueprint, request, jsonify, session, redirect
from kiteconnect import KiteConnect
from .config import Config


def create_auth_blueprint(storage):
    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/login", methods=["GET", "POST"])
    def login():

        # Browser-based login flow
        if request.method == "GET":
            kite = KiteConnect(api_key=Config.ZERODHA_API_KEY)
            return redirect(kite.login_url())

        # Existing API-based login flow
        payload = request.get_json(force=True)

        request_token = payload.get("request_token")
        user_id = payload.get("user_id", "default")

        if not request_token:
            return jsonify({
                "error": "request_token is required"
            }), 400

        kite = KiteConnect(api_key=Config.ZERODHA_API_KEY)

        try:
            session_data = kite.generate_session(
                request_token,
                Config.ZERODHA_API_SECRET
            )

        except Exception as exc:
            return jsonify({
                "error": "authentication_failed",
                "details": str(exc)
            }), 502

        access_token = session_data.get("access_token")

        if not access_token:
            return jsonify({
                "error": "missing_access_token"
            }), 500

        storage.save_access_token(user_id, access_token)

        session["user_id"] = user_id

        return jsonify({
            "message": "login_successful",
            "user_id": user_id,
            "access_token": access_token,
            "session_data": session_data,
        })

    @auth_bp.route("/callback", methods=["GET"])
    def callback():

        request_token = request.args.get("request_token")

        if not request_token:
            return jsonify({
                "error": "missing_request_token"
            }), 400

        kite = KiteConnect(api_key=Config.ZERODHA_API_KEY)

        try:

            session_data = kite.generate_session(
                request_token,
                Config.ZERODHA_API_SECRET
            )

            access_token = session_data.get("access_token")

            if not access_token:
                return jsonify({
                    "error": "missing_access_token"
                }), 500

            # Use actual Zerodha user id
            user_id = session_data.get(
                "user_id",
                Config.ZERODHA_CLIENT_ID
            )

            # Save token
            storage.save_access_token(
                user_id,
                access_token
            )

            # Create Flask session
            session["user_id"] = user_id

            # Redirect to React with auth information
            return redirect(
                f"http://localhost:5173/dashboard"
                f"?status=success"
                f"&user_id={user_id}"
            )

        except Exception as exc:

            return jsonify({
                "error": "authentication_failed",
                "details": str(exc)
            }), 502

    @auth_bp.route("/logout", methods=["POST"])
    def logout():

        session.clear()

        return jsonify({
            "message": "logout_successful"
        }), 200

    return auth_bp