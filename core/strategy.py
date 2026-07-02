from datetime import time


class ORBStrategy:
    def __init__(self, params):
        self.params = params

    def run(self, df):
        trades = []

        or_minutes = self.params["or_minutes"]

        for date, day in df.groupby(df["timestamp ET"].dt.date):

            # Keep only RTH
            day = day.copy().reset_index(drop=True)

            # Opening Range
            opening_range = day.iloc[:or_minutes]

            or_high = opening_range["high"].max()
            or_low = opening_range["low"].min()

            print(
                f"{date} | "
                f"OR High: {or_high:.2f} | "
                f"OR Low: {or_low:.2f}"
            )

        return trades