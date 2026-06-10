import sqlite3
import threading
import json
from pathlib import Path


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


class Storage:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.lock = threading.Lock()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = dict_factory
        return conn

    def init_db(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_tokens (
                    user_id TEXT PRIMARY KEY,
                    access_token TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    active INTEGER NOT NULL,
                    ema_period INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    entry_buffer_percent REAL NOT NULL,
                    profit_targets TEXT NOT NULL,
                    stop_loss REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    entry_price REAL NOT NULL,
                    status TEXT NOT NULL,
                    target_stage INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(strategy_id) REFERENCES strategies(id)
                )
                """
            )
            conn.commit()

    def save_access_token(self, user_id, access_token, created_at=None):
        created_at = created_at or __import__("datetime").datetime.utcnow().isoformat()
        with self.lock, self._connect() as conn:
            conn.execute(
                "REPLACE INTO session_tokens (user_id, access_token, created_at) VALUES (?, ?, ?)",
                (user_id, access_token, created_at),
            )
            conn.commit()

    def get_access_token(self, user_id="default"):
        with self.lock, self._connect() as conn:
            row = conn.execute(
                "SELECT access_token FROM session_tokens WHERE user_id = ?", (user_id,)
            ).fetchone()
            return row["access_token"] if row else None

    def save_strategy(self, symbol, ema_period, quantity, entry_buffer_percent, profit_targets, stop_loss, active=1, created_at=None):
        created_at = created_at or __import__("datetime").datetime.utcnow().isoformat()
        profit_targets_json = json.dumps(profit_targets)
        with self.lock, self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO strategies (symbol, active, ema_period, quantity, entry_buffer_percent, profit_targets, stop_loss, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (symbol, active, ema_period, quantity, entry_buffer_percent, profit_targets_json, stop_loss, created_at),
            )
            conn.commit()
            return cursor.lastrowid

    def get_active_strategies(self):
        with self.lock, self._connect() as conn:
            rows = conn.execute("SELECT * FROM strategies WHERE active = 1").fetchall()
            for row in rows:
                row["profit_targets"] = json.loads(row["profit_targets"])
            return rows

    def deactivate_strategy(self, strategy_id):
        with self.lock, self._connect() as conn:
            conn.execute("UPDATE strategies SET active = 0 WHERE id = ?", (strategy_id,))
            conn.commit()

    def save_position(self, strategy_id, symbol, quantity, entry_price, status="open", target_stage=0, created_at=None):
        created_at = created_at or __import__("datetime").datetime.utcnow().isoformat()
        with self.lock, self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO positions (strategy_id, symbol, quantity, entry_price, status, target_stage, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (strategy_id, symbol, quantity, entry_price, status, target_stage, created_at),
            )
            conn.commit()
            return cursor.lastrowid

    def update_position(self, position_id, status=None, target_stage=None):
        updates = []
        params = []
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if target_stage is not None:
            updates.append("target_stage = ?")
            params.append(target_stage)
        if not updates:
            return
        params.append(position_id)
        with self.lock, self._connect() as conn:
            conn.execute(f"UPDATE positions SET {', '.join(updates)} WHERE id = ?", tuple(params))
            conn.commit()

    def get_open_positions(self):
        with self.lock, self._connect() as conn:
            return conn.execute("SELECT * FROM positions WHERE status = 'open'").fetchall()
