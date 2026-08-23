from ast import comprehension
from data.consts import (
    STOCK_PATH,
    INDEX_PATH,
)
import shutil
import logging
import os
from enum import Enum
import pandas as pd
from typing import Set, Optional, Tuple
import pyarrow.parquet as pq
from pyarrow import Table

class DataType(Enum):
    STOCK = 1
    INDEX = 2

class DataFormat(Enum):
    CSV = 1
    PARQUET = 2

logger = logging.getLogger(__name__)

class StockDataStore:
    """
    local file-based data store
    """
    def __init__(self,
        stock_path:str=STOCK_PATH,
        index_path:str=INDEX_PATH,
    ):
        self.stock_path_parquet = os.path.join(stock_path, "all_stocks")
        self.index_path_parquet = os.path.join(index_path, "all_index")
        self.stock_path_csv = os.path.join(stock_path, "csv")
        self.index_path_csv = os.path.join(index_path, "csv")
        # ensure the path exists
        os.makedirs(self.stock_path_parquet, exist_ok=True)
        os.makedirs(self.index_path_parquet, exist_ok=True)
        os.makedirs(self.stock_path_csv, exist_ok=True)
        os.makedirs(self.index_path_csv, exist_ok=True)


    def save_data(self,
        ts_code: str,
        data_df: pd.DataFrame,
        format: DataFormat=DataFormat.PARQUET) -> str | None:
        """
        write data frame (from fetcher) into local file-based store
        """
        if data_df is None or data_df.empty:
            return None
        # csv data is mainly for debugging purpose
        # we use parquet for production
        if format == DataFormat.PARQUET:
            partition_path = os.path.join(f"{self.stock_path_parquet}", f"ts_code={ts_code}")
            if os.path.exists(partition_path):
                logger.debug(f"{partition_path} exists, will be deleted first")
                shutil.rmtree(partition_path)
            data_df.to_parquet(
                self.stock_path_parquet, compression="snappy", partition_cols=["ts_code"])
            logger.info(f"saved parquet {ts_code} to {partition_path}")
            return partition_path
        if format == DataFormat.CSV:
            csv_path = os.path.join(self.stock_path_csv, f"{ts_code}.csv")
            data_df.to_csv(csv_path, index=False)
            return csv_path


    def list_cached_stocks(self) -> Optional[Set[str]]:
        """
        List cached parquet data. We use parquet data for production; CSV is only for inspection
        """
        stocks: Set[str] = set()
        try:
            for _, dirs, _ in os.walk(self.stock_path_parquet):
                for d in dirs:
                    if d.startswith("ts_code="):
                        ts_code = d.split("=")[1]
                        stocks.add(ts_code)
            return stocks
        except Exception as e:
            logger.error(f"failed to list stocks from data store")


    def get_date_range(
        self,
        ts_code:str,
        data_type:DataType=DataType.STOCK) -> Optional[Tuple[str, str]]:
        """
        Get date range of a given stock/index

        Args:
            ts_code: the stock's ts_code
            data_type: DataType.STOCK or DataType.INDEX

        Returns:
            A tuple of `(start_date, end_date)` for the stock/list record in the store
            or None if there's no matching record
        """
        data_df = self.load_daily(data_type=data_type, filters=("ts_code", "=", ts_code))
        if data_df is None:
            logger.error(f"failed to get date range for the stock {ts_code}")
            return None
        min_date, max_date = data_df["trade_date"].min(), data_df["trade_date"].max()
        if pd.isna(min) or pd.isna(max):
            return None
        return (min_date, max_date)


    def update_data_batch(
        self,
        data_df: pd.DataFrame,
        data_type: DataType=DataType.STOCK) -> None:
        """
        update the data by combining the newly fetched data and the old one, and
        replacing the current files altogether

        Args:
            data_df: Newly fetched stock/index data
            data_type: DataType.STOCK or DataType.INDEX
        """
        data_path = self.stock_path_parquet if data_type == DataType.STOCK else self.index_path_parquet
        # load current data
        dataset = pq.ParquetDataset(data_path)
        old_data = dataset.read().to_pandas()

        # be careful, when there's no data in the store, it will drop all data
        data_df = data_df[data_df["ts_code"].isin(old_data["ts_code"].unique())]

        # combine old and new data
        combined_data = pd.concat([old_data, data_df], ignore_index=True) # old data first, then new data
        combined_data = combined_data.drop_duplicates(
            subset=["ts_code", "trade_date"],
            keep="last",
        )
        combined_data = combined_data.sort_value(
            ["ts_code", "trade_date"]).reset_index(drop=True)
        # clear the whole directory
        shutil.rmtree(data_path)
        os.makedirs(data_path)
        # rewrite the whole dataset at once
        table = Table.from_pandas(combined_data)
        pq.write_to_dataset(
            table,
            root_path=data_path,
            partition_cols=["ts_code"],
            comprehension="snappy",
            max_partitions=6000 # we have 5398 stocks so far
        )
        logger.info(f"Bulk update data: added {len(data_df)} new records, \
            total {len(combined_data)} records (deduplicated)")

    def load_daily(
        self,
        data_type: DataType=DataType.STOCK,
        filters: Optional[Tuple]=None,
    ) -> Optional[pd.DataFrame]:
        data_path = self.stock_path_parquet if data_type == DataType.STOCK else self.index_path_parquet
        if filters:
            dataset = pq.ParquetDataset(data_path, filters=[filters])
        else:
            dataset = pq.ParquetDataset(data_path)
        df = dataset.read().to_pandas()
        return df
