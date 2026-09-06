import numpy as np
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


def compute_bollinger_bands(
    df: pd.DataFrame, period: int = 20, std_dev: float = 2.0
) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)
    close = df["adj_close"]

    mid = close.rolling(window=period).mean()
    rolling_std = close.rolling(window=period).std(ddof=0)  # ddof=0 for population std

    upper = mid + rolling_std * std_dev
    lower = mid - rolling_std * std_dev
    diff_ul = upper - lower

    bb_width = diff_ul / mid.replace(0, np.nan)
    bb_position = (close - lower) / diff_ul.replace(0, np.nan)

    # visualization features
    result["close"] = df["adj_close"]
    result["trade_date"] = df["trade_date"]
    result["bb_upper"] = upper
    result["bb_lower"] = lower
    result["bb_mid"] = mid

    # training features
    result["bb_width"] = bb_width
    result["bb_position"] = bb_position
    return result


def compute_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)
    low = df["adj_low"]
    high = df["adj_high"]
    close = df["adj_close"]

    # calculate min/max price in n day window
    low_n = low.rolling(window=n).min()
    high_n = high.rolling(window=n).max()

    denominator = high_n - low_n
    rsv = pd.Series(np.nan, index=df.index)
    valid = denominator.notna()
    is_flat = valid & (denominator == 0)
    is_normal = valid & (denominator != 0)
    # RSV: Raw Stochastic Value
    rsv.loc[is_flat] = 50.0
    rsv.loc[is_normal] = (
        (close[is_normal] - low_n[is_normal]) / denominator[is_normal] * 100
    )
    # k: smoothed rsv
    k = rsv.ewm(alpha=1 / m1, adjust=False).mean()
    # d = k.ewm(alpha=1 / m2, adjust=False).mean()
    # j = 3 * k + 2 * d

    # visualization features
    result["trade_date"] = df["trade_date"]
    result["open"] = df["adj_open"]
    result["close"] = df["adj_close"]
    result["low"] = df["adj_low"]
    result[f"kdj_low_{n}"] = low_n
    result[f"kdj_high_{n}"] = high_n

    result["kdj_k"] = k
    # result["kdj_d"] = d
    # result["kdj_j"] = j
    return result
