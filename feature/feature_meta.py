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
    "turnover": FeatureMeta(neutralize=True),
    "industry": FeatureMeta(categorical=True),
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
    "ma_120_bias": FeatureMeta(winsorize=True, neutralize=True),
    "return_120d": FeatureMeta(winsorize=True, neutralize=True),
    "ma_5_10_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "ma_10_20_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "ma_20_60_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "ma_60_120_ratio": FeatureMeta(winsorize=True, neutralize=True),
    "up_ratio_5d": FeatureMeta(weekly=True),
    "up_ratio_20d": FeatureMeta(weekly=True),
}
