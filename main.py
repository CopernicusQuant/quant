import logging

from data import DataStore

logging.basicConfig(level=logging.INFO)


def main():
    store = DataStore()
    store.load_stocks()


if __name__ == "__main__":
    main()
