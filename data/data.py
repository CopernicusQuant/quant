import logging
import os
import shutil
from pathlib import Path

import pandas as pd
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

    def get_stock_list(self) -> pd.DataFrame:
        stock_list_path = Path(self._local_stock_list_path())
        if not stock_list_path.exists():
            logger.info("downloading stock list from R2 storage...")
            with (
                self.fs.open_input_file(self._r2_stock_list_path()) as source,
                stock_list_path.open("wb") as target,
            ):
                shutil.copyfileobj(source, target)
        df = pd.read_csv(stock_list_path)
        return df

    def _ensure_local_dirs(self):
        for folder in [INDEX_DIR, STOCK_DIR, META_DIR]:
            os.makedirs(
                f"{LOCAL_DATA_FOLDER}/{self.bucket_name}/{folder}", exist_ok=True
            )

    def _r2_stock_list_path(self) -> str:
        return f"{self.bucket_name}/{META_DIR}/{self.stock_list_filename}.csv"

    def _local_stock_list_path(self) -> str:
        return f"{LOCAL_DATA_FOLDER}/{self._r2_stock_list_path()}"
