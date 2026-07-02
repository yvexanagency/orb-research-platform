class ORBStrategy:
    def __init__(self, params):
        self.params = params

    def run(self, df):
        trades = []

        or_minutes = self.params["or_minutes"]

        for date, day in df.groupby(df["timestamp ET"].dt.date):

            day = day.reset_index(drop=True)

            # Skip incomplete sessions
            if len(day) < 391:
                continue

            opening_range = day.iloc[:or_minutes]

            or_high = opening_range["high"].max()
            or_low = opening_range["low"].min()

            entered = False

            for _, candle in day.iloc[or_minutes:].iterrows():

                # LONG
                if not entered and candle["high"] > or_high:
                    trades.append({
                        "date": date,
                        "side": "LONG",
                        "entry_time": candle["timestamp ET"],
                        "entry_price": or_high
                    })
                    entered = True
                    break

                # SHORT
                if not entered and candle["low"] < or_low:
                    trades.append({
                        "date": date,
                        "side": "SHORT",
                        "entry_time": candle["timestamp ET"],
                        "entry_price": or_low
                    })
                    entered = True
                    break

        return trades