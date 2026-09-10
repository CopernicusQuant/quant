class FeatureMeta:
    __slots__ = ["categorical", "neutralize", "weekly", "winsorize"]

    def __init__(
        self,
        categorical: bool = False,
        winsorize: bool = False,
        neutralize: bool = False,
        weekly: bool = False,
    ) -> None:
        self.categorical = categorical
        self.winsorize = winsorize
        self.neutralize = neutralize  # industry-level neutralize
        self.weekly = weekly

    def __repr__(self) -> str:
        return f"FeatureMeta(categorical={self.categorical}, winsorize={self.winsorize}, neutralize={self.neutralize}, weekly={self.weekly})"


FEATURE_META_COLLECTION = {
    # ./calculator_utils/combine_stock_basics
    "ts_code": FeatureMeta(categorical=True),
    "trade_date": FeatureMeta(categorical=True),
    "industry": FeatureMeta(categorical=True),
    "turnover": FeatureMeta(winsorize=True, neutralize=True),
    "pb": FeatureMeta(winsorize=True, neutralize=True),
    "pe": FeatureMeta(winsorize=True, neutralize=True),
    "roe": FeatureMeta(winsorize=True, neutralize=True),
    # ./calculator_utils/compute_price_momentum
    "ma_5_bias": FeatureMeta(winsorize=True, neutralize=True),
    "return_5d": FeatureMeta(winsorize=True, neutralize=True),
    "ma_10_bias": FeatureMeta(winsorize=True, neutralize=True),
    "return_10d": FeatureMeta(winsorize=True, neutralize=True),
    "ma_20_bias": FeatureMeta(winsorize=True, neutralize=True),
    "return_20d": FeatureMeta(winsorize=True, neutralize=True),
    "ma_60_bias": FeatureMeta(winsorize=True, neutralize=True),
    "return_60d": FeatureMeta(winsorize=True, neutralize=True),
    "ma_5_10_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "ma_10_20_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "ma_20_60_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "up_ratio_5d": FeatureMeta(winsorize=True, neutralize=True),
    "up_ratio_20d": FeatureMeta(winsorize=True, neutralize=True),
    # ./calculator_utils/compute_volume_momentum
    "vol_ma_5_bias": FeatureMeta(winsorize=True, neutralize=True),
    "vol_change_5d": FeatureMeta(winsorize=True, neutralize=True),
    "vol_ma_10_bias": FeatureMeta(winsorize=True, neutralize=True),
    "vol_change_10d": FeatureMeta(winsorize=True, neutralize=True),
    "vol_ma_20_bias": FeatureMeta(winsorize=True, neutralize=True),
    "vol_change_20d": FeatureMeta(winsorize=True, neutralize=True),
    "vol_ma_60_bias": FeatureMeta(winsorize=True, neutralize=True),
    "vol_change_60d": FeatureMeta(winsorize=True, neutralize=True),
    "vol_ma_5_10_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "vol_ma_10_20_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "vol_ma_20_60_ratio": FeatureMeta(winsorize=True, neutralize=True),
    # ./calculator_utils/compute_activity_features
    "amplitude": FeatureMeta(winsorize=True, neutralize=True),
    "amplitude_ma_5": FeatureMeta(winsorize=True, neutralize=True),
    "amplitude_ma_20": FeatureMeta(winsorize=True, neutralize=True),
    "amplitude_quantile_60": FeatureMeta(neutralize=True),
    "turnover_ma_5_bias": FeatureMeta(winsorize=True, neutralize=True),
    "turnover_ma_20_bias": FeatureMeta(winsorize=True, neutralize=True),
    "turnover_quantile_60": FeatureMeta(neutralize=True),
    "activity_score_60": FeatureMeta(neutralize=True),
    "thin_trade_amplitude_score_60": FeatureMeta(neutralize=True),
    "turnover_without_move_score_60": FeatureMeta(neutralize=True),
}
