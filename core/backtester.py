from core.simulator import Simulator
from core.strategy import ORBStrategy


class Backtester:
    """Coordinates the pipeline. No business logic should live here."""

    def __init__(self, df, config):
        self.df = df
        self.config = config

    def run(self):

        strategy = ORBStrategy(self.config)
        simulator = Simulator(self.config)

        completed_trades = []

        for signal in strategy.run(self.df):
            completed_trades.append(simulator.run(signal))

        return completed_trades
