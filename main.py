import logging

from data import DataStore

logging.basicConfig(level=logging.INFO)


def main():
    store = DataStore()
    stock_list_df = store.get_stock_list()
    print(stock_list_df.head(3))


if __name__ == "__main__":
    main()
