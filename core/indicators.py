import pandas as pd


def add_indicators(df, atr_period=14):
    df = df.copy()

    for period in [20, 50, 100, 200]:
        df[f"EMA_{period}"] = (
            df["close"]
            .ewm(span=period, adjust=False)
            .mean()
        )

    df["ATR"] = _average_true_range(df, atr_period)

    return df


def _average_true_range(df, period):
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)

    true_range = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.rolling(window=period, min_periods=1).mean()
