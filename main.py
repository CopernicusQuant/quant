import logging

from data import DataStore
from feature.calculator_utils import (
    combine_stock_basics,
    compute_bollinger_bands,
    compute_dema,
    compute_kdj,
    compute_macd,
    compute_obv,
    compute_price_momentum,
    compute_rsi,
)
from visualization.plot import (
    vis_bollinger_bands,
    vis_dema,
    vis_kdj,
    vis_macd,
    vis_obv_flow,
    vis_rsi,
)
from visualization.price_momentum import vis_price_momentum

logging.basicConfig(level=logging.INFO)


def main():
    store = DataStore()
    # store.download_stocks()
    # store.load_stocks()
    stock = store.load_single_stock(
        ts_code="AAPL",
    )
    # info = store.get_stock_list()
    # stock_info = info[info["ts_code"] == "GOOG"]
    # result = combine_stock_basics(stock_data_df=stock, stock_info_df=stock_info)
    stock.set_index("trade_date", inplace=True)
    result = compute_price_momentum(stock)
    vis_price_momentum(stock, result[result.index >= "20250910"])


if __name__ == "__main__":
    main()
