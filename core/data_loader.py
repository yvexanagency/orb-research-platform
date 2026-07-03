import pandas as pd


def load_data(path, session_start="09:30", session_end="16:00"):
    df = pd.read_csv(path)

    df["timestamp ET"] = pd.to_datetime(
        df["timestamp ET"],
        format="%m/%d/%Y %H:%M"
    )

    df = df.sort_values("timestamp ET").reset_index(drop=True)

    start_t = pd.Timestamp(session_start).time()
    end_t = pd.Timestamp(session_end).time()

    # Keep only Regular Trading Hours
    df = df[
        (df["timestamp ET"].dt.time >= start_t) &
        (df["timestamp ET"].dt.time <= end_t)
    ].reset_index(drop=True)

    return df
