from data import DataType
from data.data_store import StockDataStore
import pytest

store:StockDataStore

def setup_module(module):
    global store
    store = StockDataStore()

def teardown_module(module):
    pass

@pytest.fixture(scope="function", autouse=True)
def before_every_test():
    print()
    yield
    print()

# uv run pytest ./tests/test_data/test_data_store.py::test_list_cached_stocks -v -s
def test_list_cached_stocks():
    stocks = store.list_cached_stocks()
    print(stocks)

# uv run pytest ./tests/test_data/test_data_store.py::test_get_date_range -v -s
def test_get_date_range():
    date_range = store.get_date_range(
        ts_code="AVGO", data_type=DataType.STOCK)
    print(date_range)
