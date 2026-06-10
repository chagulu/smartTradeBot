from apscheduler.schedulers.background import BackgroundScheduler


class WorkerEngine:
    def __init__(self, strategy_engine, interval_seconds=15):
        self.strategy_engine = strategy_engine
        self.interval_seconds = interval_seconds
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.add_job(
            self.strategy_engine.evaluate_active_strategies,
            trigger="interval",
            seconds=self.interval_seconds,
            id="strategy_evaluator",
            replace_existing=True,
        )
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown(wait=False)
