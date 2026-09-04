import logging

from data import DataStore
from feature.calculator import compute_dema
from visualization.plot import vis_dema

logging.basicConfig(level=logging.INFO)


def main():
    store = DataStore()
    # store.load_stocks()
    stock = store.load_single_stock(
        ts_code="MO",
    )
    result = compute_dema(stock, 20, 120)
    vis_dema(result)


if __name__ == "__main__":
    main()
