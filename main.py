import logging

from data import DataStore
from feature import FeatureCalculator

logging.basicConfig(level=logging.INFO)


def main():
    store = DataStore()
    feature_calculator = FeatureCalculator()

    # ts_code = "AAPL"
    # info = store.get_stock_list()

    # stock_data_df = store.load_single_stock(ts_code=ts_code)
    # stock_info_df = info[info["ts_code"] == ts_code]
    # feature_df = feature_calculator.compute_stock_features(
    #     stock_data_df=stock_data_df, stock_info_df=stock_info_df
    # )
    # store.save_single_feature(ts_code=ts_code, feature_df=feature_df)


if __name__ == "__main__":
    main()
