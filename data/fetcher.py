import json
from pathlib import Path
import requests
import logging
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import tushare as ts

from utils.config import load_config

logger = logging.getLogger(__name__)

STOCK_LIST_FILENAME = "stock_list_sec.csv"
STOCK_LIST_TUSHARE_FILENAME = "stock_list_tushare.csv"
STOCK_METADATA_FILENAME = "stock_list_meta.csv"
ENRICHED_STOCK_LIST_FILENAME = "stock_list_with_metadata.csv"

# Should provide your real name and contact email
SEC_HEADERS = {
    "User-Agent": "MyQuantApp admin@myproject.com"
}

class StockDataFetcher:
    """Tushare data fetcher"""

    def __init__(self, config: dict | None = None):
        if config is None:
            config = load_config()
            tushare_config = config["tushare"]

        ts.set_token(tushare_config.get("token"))
        self.tushare_pro = ts.pro_api()
        logger.info("StockDataFetcher initialized")

        # setup data output folder
        output_folder = Path(__file__).resolve().parent / "output"
        self.output_folder = output_folder
        self.output_folder.mkdir(parents=True, exist_ok=True)


    def get_us_daily(
        self, ts_code: str, start_date: str = "20050101", end_date: str = ""
    ) -> pd.DataFrame:
        """A much more comprehensive way getting us stock daily data
        Return Fields: ts_code,trade_date,close,turnover,pe,pb,[ps],total_share,total_mv,roe
        """
        end_date = (
            datetime.now(tz=ZoneInfo("America/New_York")).strftime("%Y%m%d")
            if not end_date
            else end_date
        ) # end date defaults to "today" if not provided
        if not ts_code and start_date != end_date:
            raise ValueError(
                "tushare us_daily(): either provide a ts_code or set the start/end date the same day"
            )
        if (int(end_date) - int(start_date)) // 10000 > 23:
            raise ValueError(
                "tushare us_daily(): time span should not more than 23 years"
            )
        try_times = 0
        success = False
        exception = None
        while try_times < 3:
            try:
                # this api returns 6000 rows in maximum; can retrieve full data through pagination
                df = self.tushare_pro.us_daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date,
                    fields=[
                        "ts_code",
                        "trade_date",
                        "close",
                        "turnover_ratio",
                        "pe",
                        "pb",
                        "total_mv",
                        "amount",
                    ],
                )
            except Exception as e:
                exception = e
                try_times += 1
                time.sleep(30)
                continue
            else:
                success = True
                break
        if not success:
            logger.error(f"Failed to fetch us_daily of {ts_code}: {str(exception)}")
            return pd.DataFrame()

        df["roe"] = df["pb"] / df["pe"]
        df["total_share"] = df["total_mv"] / df["close"]
        df = df.rename(columns={"turnover_ratio": "turnover"})
        df = df.sort_values("trade_date").reset_index(drop=True)
        return df


    def get_stock_list_data(self, refresh:bool=False, limits:int=0) -> pd.DataFrame:
        # check sec stock list file
        sec_stock_list_file = self.output_folder / STOCK_LIST_FILENAME
        if sec_stock_list_file.exists() and not refresh:
            logger.info("found local stock list file")
            df_sec = pd.read_csv(sec_stock_list_file)
        else:
            df_sec = self._fetch_stock_list_sec()
            time.sleep(0.12) # sec has a 10 req/min limit

        # check tushare stock list file
        tushare_stock_list_file = self.output_folder / STOCK_LIST_TUSHARE_FILENAME
        if tushare_stock_list_file.exists() and not refresh:
            logger.info("found local tushare stock list file")
            df_tushare = pd.read_csv(tushare_stock_list_file)
        else:
            df_tushare = self._fetch_stock_list_tushare()

        # check stock metadata file
        stock_meta_file = self.output_folder / STOCK_METADATA_FILENAME
        if stock_meta_file.exists() and not refresh:
            logger.info("found local stock metadata file")
            df_metadata = pd.read_csv(stock_meta_file)
        else:
            cik_list = df_sec["cik"].tolist()
            if (limits > 0):
                cik_list = cik_list[:limits]
            df_metadata = self._fetch_all_stock_metadata(cik_list=cik_list)

        # merge two files
        df_full = self._merge_stock_list_meta(
            df_sec=df_sec,
            df_tushare=df_tushare,
            df_metadata=df_metadata)
        output_file = self.output_folder / ENRICHED_STOCK_LIST_FILENAME
        df_full.to_csv(output_file, index=False)
        return df_full

    def _merge_stock_list_meta(self, df_sec: pd.DataFrame, df_tushare: pd.DataFrame, df_metadata: pd.DataFrame) -> pd.DataFrame:
        df_tushare.dropna(subset=["ts_code", "list_date"], inplace=True)
        df_tushare.drop(columns=["enname"], inplace=True)
        df_metadata.dropna(subset=["ts_code", "sic_code", "exchange"], inplace=True)
        df_metadata.drop(columns=["cik"], inplace=True)
        df_metadata["sic_code"] = df_metadata["sic_code"].astype(int)
        df_full = df_sec.merge(
            df_metadata,
            on="ts_code",
            how="inner",
        )
        df_full = df_full.merge(
            df_tushare,
            on="ts_code",
            how="inner"
        )
        df_full.drop_duplicates(["ts_code"], inplace=True)
        df_full = df_full[~(df_full["exchange"] == "OTC")].reset_index(drop=True)
        df_full["sector"] = df_full["sic_code"].apply(self._sic_sector)
        return df_full

    def _fetch_stock_list_sec(self) -> pd.DataFrame:
        """Fetch full us stock list from sec
        Return Fields: cik, ts_code, company_name
        """
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=SEC_HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        df_sec = pd.DataFrame.from_dict(data, orient="index")
        df_sec.rename(
            columns={
                "cik_str":"cik",
                "ticker": "ts_code",
                "title": "company_name"},
            inplace=True
        )
        # Save the DataFrame as a csv file into data/output/
        output_file = self.output_folder / STOCK_LIST_FILENAME
        df_sec.to_csv(output_file, index=False)
        return df_sec

    def _fetch_stock_list_tushare(self) -> pd.DataFrame:
        """Get stock list from tushare, this data provides list date and classify info
        """
        all_dfs = []
        limit = 6000
        offset = 0
        while True:
            df = self.tushare_pro.us_basic(
                offset=offset,
                limit=limit,
                list_status="L",
                fields=["ts_code", "list_date", "enname", "classify"]
            )
            # if df is empty, it means that the scan has completed
            if df is None or df.empty:
                break
            all_dfs.append(df)
            # if the number of data is less than limit, it also means the scan has completed
            if len(df) < limit:
                break
            offset += limit
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.dropna(subset=["ts_code", "list_date"], inplace=True)
        final_df["list_date"] = final_df["list_date"].astype("string")
        output_file = self.output_folder / STOCK_LIST_TUSHARE_FILENAME
        final_df.to_csv(output_file, index=False)
        return final_df

    def _fetch_all_stock_metadata(self, cik_list: list[int]) -> pd.DataFrame:
        """Get all stock metadata one by one for the stocks from cik_list
        """
        metadata_rows = []
        num_fetched = 0
        for cik in cik_list:
            result = self._fetch_single_stock_metadata(cik)
            if result == None:
                break
            metadata_rows.append(result)
            num_fetched += 1
            if num_fetched % 10 == 0:
                logger.info(f"===== num metadata fetched: {num_fetched} =====")
            time.sleep(0.12) # sec has a 10 req/min limit
        df_metadata = pd.DataFrame(metadata_rows)
        df_metadata.rename(columns={"ticker": "ts_code"}, inplace=True)
        output_file = self.output_folder / STOCK_METADATA_FILENAME
        self.output_folder.mkdir(parents=True, exist_ok=True)
        df_metadata.to_csv(output_file, index=False)
        return df_metadata

    def _fetch_single_stock_metadata(self, cik: int) -> dict | None:
        """Fetch single stock metadata from sec.
        Return Fields: cik, ticker, exchange, sic_code, industry
        """
        cik_padded = str(cik).zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
        response = requests.get(url, headers=SEC_HEADERS, timeout=30)

        if response.status_code != 200:
            logger.warning(
                "failed to fetch metadata for CIK %s: %s",
                cik_padded,
                response.status_code
            )
            return None

        data = response.json()
        tickers = data.get("tickers", [])
        exchanges = data.get("exchanges", [])
        return  {
            "cik": cik,
            "ticker": tickers[0] if tickers else None,
            "exchange": exchanges[0] if exchanges else None,
            "sic_code": data.get("sic"),
            "industry": data.get("sicDescription")
        }

    def _sic_sector(self, sic_code:int) -> str:
        code = sic_code // 100
        if 1 <= code <= 9:
            return "Agriculture, Forestry, Fishing"
        if 10 <= code <= 14:
            return "Mining"
        if 15 <= code <= 17:
            return "Construction"
        if 20 <= code <= 39:
            return "Manufacturing"
        if 40 <= code <= 49:
            return "Transportation, Utilities"
        if 50 <= code <= 51:
            return "Wholesale Trade"
        if 52 <= code <= 59:
            return "Retail Trade"
        if 60 <= code <= 67:
            return "Finance, Insurance, Real Estate"
        if 70 <= code <= 89:
            return "Services"
        if 91 <= code <= 97:
            return "Public Administration"
        if code == 99:
            return "Nonclassifiable"
        return "Unknown"
