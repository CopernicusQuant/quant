import logging

from data import DataStore
from feature.calculator_utils import (
    # compute_rsi,
    # combine_stock_basics,
    # compute_bollinger_bands,
    # compute_dema,
    # compute_kdj,
    # compute_macd,
    # compute_obv,
    # compute_price_momentum,
    # compute_volume_momentum,
    # compute_activity_features,
    # compute_volatility,
    compute_cci,
)

# from visualization.plot import (
# vis_bollinger_bands,
# vis_dema,
# vis_kdj,
# vis_macd,
# vis_obv_flow,
# vis_rsi,
# )
# from visualization.price_momentum import vis_price_momentum
# from visualization.volume_momentum import vis_volume_momentum
# from visualization.activity import vis_activity_features
# from visualization.volatility import vis_volatility
from visualization.cci import vis_cci

logging.basicConfig(level=logging.INFO)


def main():
    store = DataStore()
    # store.download_stocks()
    # store.load_stocks()
    stock = store.load_single_stock(
        ts_code="GOOG",
    )
    # info = store.get_stock_list()
    # stock_info = info[info["ts_code"] == "GOOG"]
    # result = combine_stock_basics(stock_data_df=stock, stock_info_df=stock_info)
    stock.set_index("trade_date", inplace=True)
    # result = compute_activity_features(stock)
    # vis_activity_features(stock, result)

    # print(stock.head(20))
    # result = compute_price_momentum(stock)
    # vis_price_momentum(stock, result[result.index >= "20250810"])
    # result = compute_volume_momentum(stock)
    # vis_volume_momentum(stock, result[result.index >= "20250910"])
    # result = compute_volatility(stock)
    # vis_volatility(stock, result)
    result = compute_cci(stock)
    vis_cci(stock_df=stock, cci_df=result)
    # print(result.tail(30))


if __name__ == "__main__":
    main()
