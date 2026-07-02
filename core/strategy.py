from core.trade import Trade


class ORBStrategy:

    def __init__(self, params):
        self.params = params

    def run(self, df):

        trades = []

        or_minutes = self.params["or_minutes"]

        for date, day in df.groupby(df["timestamp ET"].dt.date):

            day = day.reset_index(drop=True)

            if len(day) < 391:
                continue

            opening_range = day.iloc[:or_minutes]

            or_high = opening_range["high"].max()
            or_low = opening_range["low"].min()

            entered = False

            for _, candle in day.iloc[or_minutes:].iterrows():

                if entered:
                    break

                # LONG
                if candle["high"] > or_high:

                    trade = Trade(
                        date=date,
                        side="LONG",
                        entry_time=candle["timestamp ET"],
                        entry_price=float(or_high)
                    )

                    trades.append(trade)
                    entered = True

                # SHORT
                elif candle["low"] < or_low:

                    trade = Trade(
                        date=date,
                        side="SHORT",
                        entry_time=candle["timestamp ET"],
                        entry_price=float(or_low)
                    )

                    trades.append(trade)
                    entered = True

        return trades