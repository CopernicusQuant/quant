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
    result["close"] = df["adj_close"]
    result["trade_date"] = df["trade_date"]
    result["dema_fast"] = dema_fast
    result["dema_slow"] = dema_slow
    result["dema_spread"] = spread
    result["dema_gold"] = (spread.shift(1) <= 0) & (spread > 0)
    result["dema_dead"] = (spread.shift(1) >= 0) & (spread < 0)
    return result
