import pandas as pd

from .calculator_utils import (
    combine_stock_basics,
    compute_activity_features,
    compute_bollinger_bands,
    compute_cci,
    compute_dema,
    compute_kdj,
    compute_macd,
    compute_obv,
    compute_price_momentum,
    compute_rsi,
    compute_volatility,
    compute_volume_momentum,
)
from .feature_meta import FEATURE_META_COLLECTION


class FeatureCalculator:
    def __init__(self):
        self.feature_meta = FEATURE_META_COLLECTION

    def compute_stock_features(
        self, stock_data_df: pd.DataFrame, stock_info_df
    ) -> pd.DataFrame:
        new_features = [
            combine_stock_basics(
                stock_data_df=stock_data_df, stock_info_df=stock_info_df
            ),
            compute_bollinger_bands(df=stock_data_df),
            compute_activity_features(df=stock_data_df),
            compute_cci(df=stock_data_df),
            compute_dema(df=stock_data_df),
            compute_kdj(df=stock_data_df),
            compute_macd(df=stock_data_df),
            compute_obv(df=stock_data_df),
            compute_price_momentum(df=stock_data_df),
            compute_rsi(df=stock_data_df),
            compute_volatility(df=stock_data_df),
            compute_volume_momentum(df=stock_data_df),
        ]
        result = pd.concat(new_features, axis=1)
        return result.sort_index()
