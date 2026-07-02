class ORBStrategy:
    def __init__(self, params):
        self.params = params

    def run(self, df):
        trades = []

        for date, day in df.groupby(df["timestamp ET"].dt.date):
            # ORB logic will go here
            pass

        return trades