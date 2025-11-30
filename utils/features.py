import pandas as pd


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Basic feature engineering for price prediction.

    Expects df indexed by time, with columns: open, high, low, close, volume.
    """
    df = df.copy()
    df["return_1"] = df["close"].pct_change()
    df["return_5"] = df["close"].pct_change(5)
    df["vol_20"] = df["return_1"].rolling(20).std()
    df["target_up"] = (df["close"].shift(-1) > df["close"]).astype(int)
    df = df.dropna()
    return df
