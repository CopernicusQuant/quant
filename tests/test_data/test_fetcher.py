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

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_us_daily -v -s
def test_get_us_daily():
    df = fetcher.get_us_daily(ts_code="AAPL", start_date="20260409", end_date="20260416")
    print(df)
    print(",".join(df.columns.to_list()))

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_us_daily_with_list_cache -v -s
def test_get_us_daily_with_list_cache():
    fetcher.load_stock_list()
    df = fetcher.get_us_daily(ts_code="SPCX", start_date="20050101", end_date="20260701")
    print(df)
    assert str(df.iloc[0]["trade_date"]) == "20260612" # ensure don't mistakenly get prev stock sharing same ts_code
    print(",".join(df.columns.to_list()))

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_stock_list -v -s
def test_get_stock_list():
    df = fetcher.get_stock_list_data()
    print(df.head())

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_index_daily -v -s
def test_get_index_daily():
    df = fetcher.get_index_daily(ts_code="DJI", start_date="20260801", end_date="20260806")
    print(df.head())

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_trade_calendar -v -s
def test_get_trade_calendar():
    df = fetcher.get_trade_calendar(start_date="20260701", end_date="20260801")
    print(df.head())

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_next_trade_date -v -s
def test_get_next_trade_date():
    next_trade_day = fetcher.get_next_trade_date(curr_date="20260522")
    print(next_trade_day) # should be 20260526 if curr_date is 20260522
