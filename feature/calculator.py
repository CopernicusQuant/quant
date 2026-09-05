import pandas as pd


def compute_dema(
    df: pd.DataFrame, fast_period: int = 20, slow_period: int = 60
) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)
    close = df["adj_close"]
    ema1_fast = close.ewm(span=fast_period, adjust=False).mean()
    ema1_slow = close.ewm(span=slow_period, adjust=False).mean()

    ema2_fast = ema1_fast.ewm(span=fast_period, adjust=False).mean()
    ema2_slow = ema1_slow.ewm(span=slow_period, adjust=False).mean()

    dema_fast = 2 * ema1_fast - ema2_fast
    dema_slow = 2 * ema1_slow - ema2_slow

    spread = dema_fast / dema_slow - 1

    # visualization features
    result["close"] = df["adj_close"]
    result["trade_date"] = df["trade_date"]
    result[f"dema_{fast_period}_{slow_period}_fast"] = dema_fast
    result[f"dema_{fast_period}_{slow_period}_slow"] = dema_slow

    # training features
    result[f"dema_{fast_period}_{slow_period}_spread"] = spread
    result[f"dema_{fast_period}_{slow_period}_gold"] = (
        (spread.shift(1) <= 0) & (spread > 0)
    ).astype(int)
    result[f"dema_{fast_period}_{slow_period}_dead"] = (
        (spread.shift(1) >= 0) & (spread < 0)
    ).astype(int)
    return result


def compute_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)
    close = df["adj_close"]

    ema_fast = close.ewm(span=fast_period, adjust=False).mean()
    ema_slow = close.ewm(span=slow_period, adjust=False).mean()
    diff = (
        ema_fast - ema_slow
    ) / ema_slow  # divide ema_slow for the normalization purpose
    dea = diff.ewm(span=signal_period, adjust=False).mean()
    macd_hist = diff - dea
    macd_gold = ((macd_hist.shift(1) < 0) & (macd_hist > 0)).astype(int)
    macd_dead = ((macd_hist.shift(1) > 0) & (macd_hist < 0)).astype(int)

    # visualization features
    result["close"] = df["adj_close"]
    result["trade_date"] = df["trade_date"]
    result["macd_ema_slow"] = ema_slow
    result["macd_ema_fast"] = ema_fast
    result["macd_gold"] = macd_gold
    result["macd_dead"] = macd_dead

    # training features
    result["macd_diff"] = diff
    result["macd_dea"] = dea
    result["macd_hist"] = macd_hist

    return result
