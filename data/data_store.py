import shutil
import logging
import os
from enum import Enum
import pandas as pd

# Default stock data path
STOCK_PATH = "data/store/stock/"
# Default index data path
INDEX_PATH = "data/store/index/"

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
    def __init__(self, stock_path:str=STOCK_PATH, index_path:str=INDEX_PATH):
        self.stock_path_parquet = stock_path + "all_stocks"
        self.index_path_parquet = index_path + "all_index"
        self.stock_path_csv = stock_path + "/csv"
        self.index_path_csv = index_path + "/csv"
        # ensure the path exists
        os.makedirs(self.stock_path_parquet, exist_ok=True)
        os.makedirs(self.index_path_parquet, exist_ok=True)
        os.makedirs(self.stock_path_csv, exist_ok=True)
        os.makedirs(self.index_path_csv, exist_ok=True)

    def save_data(self,
        ts_code: str,
        data_df: pd.DataFrame,
        format: DataFormat=DataFormat.PARQUET) -> None:
        """
        write data frame (from fetcher) into local file-based store
        """
        if data_df is None or data_df.empty:
            return
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
            return
        if format == DataFormat.CSV:
            csv_path = os.path.join(self.stock_path_csv, f"{ts_code}.csv")
            data_df.to_csv(csv_path, index=False)
