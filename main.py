import logging

from data import DataStore
from feature.calculator import compute_bollinger_bands, compute_dema, compute_macd
from visualization.plot import vis_bollinger_bands, vis_dema, vis_macd

logging.basicConfig(level=logging.INFO)


def main():
    store = DataStore()
    # store.load_stocks()
    stock = store.load_single_stock(
        ts_code="GOOG",
    )
    # fast_period, slow_period = 20, 120
    # result = compute_dema(stock, fast_period=fast_period, slow_period=slow_period)
    # vis_dema(result, fast_period=fast_period, slow_period=slow_period)
    # result = compute_macd(stock)
    # vis_macd(result)
    result = compute_bollinger_bands(stock)
    vis_bollinger_bands(result)


if __name__ == "__main__":
    main()
