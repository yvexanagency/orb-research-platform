import pandas as pd

def add_indicators(df):
    df = df.copy()

    for period in [20, 50, 100, 200]:
        df[f"EMA_{period}"] = df["close"].ewm(span=period, adjust=False).mean()

    return df