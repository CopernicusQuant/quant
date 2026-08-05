from data.fetcher import TushareFetcher
import pytest

fetcher:TushareFetcher

def setup_module(module):
    global fetcher
    fetcher = TushareFetcher()

def teardown_module(module):
    pass

@pytest.fixture(scope="function", autouse=True)
def before_every_test():
    print()
    yield
    print()

# uv run pytest ./tests/test_data/test_fetcher.py::test_get_daily_basic -v -s
def test_get_daily_basic():
    df=fetcher.get_daily_basic(ts_code="AAPL", start_date="20260409", end_date="20260416")
    print(df)
    print(",".join(df.columns.to_list()))
