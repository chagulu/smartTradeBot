import time
import threading
from datetime import datetime

class WorkerEngine:
    def __init__(self, engine, interval_seconds=15):
        self.engine = engine
        self.interval = interval_seconds
        self.running = False
        self._thread = None
        self.last_execution_time = None

    def _run_loop(self):
        while self.running:
            try:
                print(f"[{datetime.now()}] Worker executing cycle...")
                self.engine.run_cycle()
                self.last_execution_time = datetime.now()
            except Exception as e:
                print(f"Worker cycle error: {e}")
            time.sleep(self.interval)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            print("Worker Engine started.")

    def status(self):
        return {
            "running": self.running,
            "last_execution_time": (
                self.last_execution_time.isoformat()
                if self.last_execution_time else None
            ),
            "interval_seconds": self.interval,
        }
