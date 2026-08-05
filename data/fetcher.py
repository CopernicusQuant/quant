import logging
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import tushare as ts

from utils.config import load_config

logger = logging.getLogger(__name__)


class TushareFetcher:
    """Tushare data fetcher"""

    def __init__(self, config: dict | None = None):
        if config is None:
            config = load_config()["tushare"]
        ts.set_token(config.get("token"))
        self.pro = ts.pro_api()
        logger.info("TushareFetcher initialized")


    def get_daily(self, date: str, price_col: str = "close") -> pd.Series:
        """Get the unadjusted price of every stock in the market on a given day
        Args:
            date (str): Date, format: YYYYMMDD

        Returns:
            pd.Series: ``ts_code`` as index, price as data
        """
        df = self.pro.us_daily(trade_date=date, fields=["ts_code", price_col])
        if df is None or len(df) == 0:
            return pd.Series()
        return pd.Series(index=df["ts_code"], data=df[price_col].to_list())


    def get_daily_basic(
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
                df = self.pro.us_daily(
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
