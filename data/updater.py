from datetime import datetime
import logging
from data import StockDataFetcher, StockDataStore

logger = logging.getLogger(__name__)

def incremental_update_data(
    fetcher: StockDataFetcher,
    store: StockDataStore,
):
    today = datetime.now()
    cached_stocks = store.list_cached_stocks()
    if cached_stocks is None or len(cached_stocks) == 0:
        logger.fatal("no local stock cache were found")
        return
    max_date = today
