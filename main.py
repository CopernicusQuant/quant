import logging

from data import DataStore
from feature import FeatureCalculator
from visualization import vis_activity_features, vis_bollinger_bands

logging.basicConfig(level=logging.INFO)


def main():
    store = DataStore()
    # feature_calculator = FeatureCalculator()

    ts_code = "A"
    # info = store.get_stock_list()
    # stocks = store.load_stocks()
    # result = feature_calculator.compute_all_stock_features(
    #     combined_stock_df=stocks, combined_info_df=info
    # )
    # store.save_all_features(result)
    stock_df = store.load_single_stock(ts_code=ts_code)
    feature_df = store.load_single_feature(ts_code=ts_code)
    # vis_bollinger_bands(stock_df=stock_df, bb_df=feature_df)
    vis_activity_features(stock_df=stock_df, feature_df=feature_df)


if __name__ == "__main__":
    main()
