import threading
import time

class WorkerEngine:
    def __init__(self, strategy_engine, interval_seconds=15):
        self.engine = strategy_engine
        self.interval = interval_seconds
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.running = False

    def start(self):
        self.running = True
        self.thread.start()

    def _run(self):
        while self.running:
            print(f"Worker heartbeat: Executing strategies at {time.ctime()}")
            self.engine.run_all()
            time.sleep(self.interval)