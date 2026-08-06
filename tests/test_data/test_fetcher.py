from data.fetcher import StockDataFetcher
import pytest

fetcher:StockDataFetcher

def setup_module(module):
    global fetcher
    fetcher = StockDataFetcher()

def teardown_module(module):
    pass

@pytest.fixture(scope="function", autouse=True)
def before_every_test():
    print()
    yield
    print()

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_daily_basic -v -s
def test_get_us_daily():
    df=fetcher.get_us_daily(ts_code="AAPL", start_date="20260409", end_date="20260416")
    print(df)
    print(",".join(df.columns.to_list()))

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_stock_list_data -v -s
def test_get_stock_list():
    df=fetcher.get_stock_list_data(limits=10)
    print(df.head())
