from core.simulator import Simulator
from core.strategy import ORBStrategy


class Backtester:

    def __init__(self, df, params):
        self.df = df
        self.params = params

    def run(self):

        strategy = ORBStrategy(self.params)
        simulator = Simulator(self.params)

        completed_trades = []

        for signal in strategy.run(self.df):
            completed_trades.append(simulator.run(signal))

        return completed_trades