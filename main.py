from data import StockDataFetcher, StockDataStore, DataFormat

def main():
    fetcher = StockDataFetcher(load_stock_list=True)
    store = StockDataStore()
    # temp code
    ts_codes = ["SPCX", "AMZN", "WMT", "AVGO", "AAPL"]
    for ts_code in ts_codes:
        data_df = fetcher.get_us_daily(
            ts_code=ts_code,
            start_date="20050101",
            end_date="20260620"
        )
        store.save_data(
            ts_code=ts_code,
            data_df=data_df,
            # format=DataFormat.CSV
        )

if __name__ == "__main__":
    main()
