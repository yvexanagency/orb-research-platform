class ORBStrategy:
    def __init__(self, params):
        self.params = params

    def run(self, df):
        trades = []

        grouped = df.groupby(df["timestamp ET"].dt.date)

        for date, day in grouped:
            print(f"{date} -> {len(day)} candles")

        return trades