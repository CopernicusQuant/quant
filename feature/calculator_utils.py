import itertools

import numpy as np
import pandas as pd


def combine_stock_basics(stock_data_df: pd.DataFrame, stock_info_df: pd.DataFrame):
    """
    Gather all of the basic data from the original, unmodified dataset.
    selected fields from stock_data_df: ts_code, trade_date, turnover, pb, pe, roe
    selected fields from stock_info_df: sub_industry
    output columns: ts_code, trade_date, turnover, industry

    Args:
        stock_data_df: single stock's raw data
        stock_info_df: single stock's info dataframe
    Returns:
        combined data frame
    """
    result = stock_data_df[
        ["ts_code", "trade_date", "turnover", "pb", "pe", "roe"]
    ].copy()
    result["industry"] = stock_info_df["sub_industry"].iloc[0]
    result.set_index("trade_date", inplace=True)
    return result


def compute_price_momentum(
    df: pd.DataFrame, periods: list[int] | None = None
) -> pd.DataFrame:
    """
    Calculate price change related features,
    including `ma_{period}`, `ma_{period}_bias`, `ma_{short}_{long}_ratio` `return_{period}d`
    `raise_days`, `fall_days`, `up_ratio_5d`, `up_ratio_20d`

    visualization-only features:


    Args:
        df: single stock data, with index of trade_date
        periods: a list of periods, sorted increasingly. Normally ignore this param except really need
    Returns:
        pd.DataFrame of calculated features
    """
    if periods is None:
        periods = [
            5,
            10,
            20,
            60,
            120,
        ]
    result = pd.DataFrame(index=df.index)
    close = df["adj_close"]
    for period in periods:
        ma = close.rolling(window=period, min_periods=1).mean()
        result[f"ma_{period}"] = (
            ma  # ma will not be in the feature colletion, it will be used for calculation or data visualization
        )
        result[f"ma_{period}_bias"] = (close - ma) / ma
        result[f"return_{period}d"] = close / close.shift(period) - 1
    for short, long in itertools.pairwise(periods):
        result[f"ma_{short}_{long}_ratio"] = (
            result[f"ma_{short}"] / result[f"ma_{long}"]
        )

    # Count consecutive up/down closes. A flat close breaks either streak.
    delta = close.diff()
    status = pd.Series(
        np.where(delta > 0, 1, np.where(delta < 0, -1, 0)), index=df.index
    )
    result["up_ratio_5d"] = status.eq(1).rolling(window=5, min_periods=5).mean()
    result["up_ratio_20d"] = status.eq(1).rolling(window=20, min_periods=20).mean()
    return result


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


def compute_rsi(df: pd.DataFrame, periods: list[int] | None = None) -> pd.DataFrame:
    if periods == None:
        periods = [6, 14]  # default periods

    result = pd.DataFrame(index=df.index)
    close = df["adj_close"]
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)

    for period in periods:
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        result[f"rsi_{period}"] = rsi
        result[f"rsi_{period}_over_bought"] = (rsi > 70).astype(int)
        result[f"rsi_{period}_over_sold"] = (rsi < 30).astype(int)

    # visualization features
    result["trade_date"] = df["trade_date"]
    result["close"] = close

    return result


def compute_obv(df: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)
    close = df["adj_close"]
    volume = df["adj_vol"]

    delta = close.diff()
    signed_volume = volume.where(delta > 0, -volume.where(delta < 0, 0))
    signed_volume.iloc[0] = (
        0  # set the first day as zero to avoid any wrong gain/loss sign
    )

    flow_5 = signed_volume.rolling(5, min_periods=5).sum()
    flow_20 = signed_volume.rolling(20, min_periods=20).sum()

    result["close"] = close

    # model features
    result["obv_flow_strength_5"] = flow_5 / volume.rolling(5, min_periods=5).sum()
    result["obv_flow_strength_20"] = flow_20 / volume.rolling(20, min_periods=20).sum()

    # between [2, -2]
    result["obv_strength_accel_5_20"] = (
        result["obv_flow_strength_5"] - result["obv_flow_strength_20"]
    )

    return result
