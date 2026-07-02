from core.entry_signal import EntrySignal
from core.trade import Trade


class ORBStrategy:

    def __init__(self, params):
        self.params = params

    def run(self, df):

        signals = []

        or_minutes = self.params["or_minutes"]

        for date, day in df.groupby(df["timestamp ET"].dt.date):

            day = day.reset_index(drop=True)

            if len(day) < 391:
                continue

            opening_range = day.iloc[:or_minutes]

            or_high = float(opening_range["high"].max())
            or_low = float(opening_range["low"].min())

            for idx, candle in day.iloc[or_minutes:].iterrows():

                # LONG
                if candle["high"] > or_high:

                    trade = Trade(
                        date=date,
                        side="LONG",
                        entry_time=candle["timestamp ET"],
                        entry_price=or_high
                    )

                    signals.append(
                        EntrySignal(
                            trade=trade,
                            day_data=day,
                            entry_index=idx,
                            or_high=or_high,
                            or_low=or_low
                        )
                    )

                    break

                # SHORT
                elif candle["low"] < or_low:

                    trade = Trade(
                        date=date,
                        side="SHORT",
                        entry_time=candle["timestamp ET"],
                        entry_price=or_low
                    )

                    signals.append(
                        EntrySignal(
                            trade=trade,
                            day_data=day,
                            entry_index=idx,
                            or_high=or_high,
                            or_low=or_low
                        )
                    )

                    break

        return signals