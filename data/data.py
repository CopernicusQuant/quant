import logging
import os
import shutil
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from pyarrow import fs

from config import get_config

INDEX_DIR = "index"
STOCK_DIR = "stock"
META_DIR = "meta"

STOCK_LIST_FILENAME_PREFIX = "stock_list"
LOCAL_DATA_FOLDER = "data"

logger = logging.getLogger(__name__)


class DataStore:
    def __init__(self):
        config = get_config().store
        # Setup R2 connection and filenames
        endpoint = config.bucket_endpoint.replace("https://", "").replace("http://", "")
        self.fs = fs.S3FileSystem(
            access_key=config.access_key_id,
            secret_key=config.secret_access_key,
            region="auto",
            scheme="https",
            endpoint_override=endpoint,
        )
        self.bucket_name = config.bucket_name
        self.stock_list_filename = STOCK_LIST_FILENAME_PREFIX
        if config.runtime_env == "dev":
            self.bucket_name = f"{self.bucket_name}-dev"
            self.stock_list_filename = f"{self.stock_list_filename}_dev"

        # Setup local path
        self._ensure_local_dirs()
        self._r2_stock_list_path = (
            f"{self.bucket_name}/{META_DIR}/{self.stock_list_filename}.csv"
        )
        self._r2_stocks_path = f"{self.bucket_name}/{STOCK_DIR}"
        self._local_stock_list_path = f"{LOCAL_DATA_FOLDER}/{self._r2_stock_list_path}"
        self._local_stocks_path = f"{LOCAL_DATA_FOLDER}/{self._r2_stocks_path}"

    def get_stock_list(self) -> pd.DataFrame:
        stock_list_path = Path(self._local_stock_list_path)
        if not stock_list_path.exists():
            logger.info("downloading stock list from R2 storage...")
            with (
                self.fs.open_input_file(self._r2_stock_list_path) as source,
                stock_list_path.open("wb") as target,
            ):
                shutil.copyfileobj(source, target)
        df = pd.read_csv(stock_list_path)
        return df

    def download_stocks(self):
        stock_list_df = self.get_stock_list()
        stocks = stock_list_df["ts_code"].to_list()
        for i, stock in enumerate(stocks):
            remote_file = f"{self._r2_stocks_path}/{stock}.parquet"
            local_path = f"{self._local_stocks_path}/{stock}.parquet"
            with (
                self.fs.open_input_file(remote_file) as source,
                open(local_path, "wb") as target,
            ):
                shutil.copyfileobj(source, target)
            if (i + 1) % 10 == 0:
                logger.info(f"{i + 1} stock files downloaded")
        logger.info("stock download completed")

    def load_single_stock(
        self, ts_code: str, filters: list[tuple] | None = None
    ) -> pd.DataFrame:
        stock_path = f"{self._local_stocks_path}/{ts_code}.parquet"
        table = pq.read_table(stock_path, filters=filters)
        df = table.to_pandas()
        return df

    def load_stocks(self, filters: list[tuple] | None = None) -> pd.DataFrame:
        if filters:
            dataset = pq.ParquetDataset(self._local_stocks_path, filters=filters)
        else:
            dataset = pq.ParquetDataset(self._local_stocks_path)
        table = dataset.read()
        df = table.to_pandas()
        return df

    def _ensure_local_dirs(self):
        for folder in [INDEX_DIR, STOCK_DIR, META_DIR]:
            os.makedirs(
                f"{LOCAL_DATA_FOLDER}/{self.bucket_name}/{folder}", exist_ok=True
            )
