from core.strategy import ORBStrategy


class Backtester:

    def __init__(self, df, params):
        self.df = df
        self.params = params

    def run(self):
        strategy = ORBStrategy(self.params)
        return strategy.run(self.df)