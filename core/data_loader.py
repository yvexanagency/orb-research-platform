import pandas as pd

def load_data(path):
    df = pd.read_csv(path)

    df["timestamp ET"] = pd.to_datetime(
        df["timestamp ET"],
        format="%m/%d/%Y %H:%M"
    )

    df = df.sort_values("timestamp ET").reset_index(drop=True)

    return df