import logging
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_ticker_data(ticker: str) -> pd.DataFrame:
    logging.info(f"Fetching data for {ticker}")

    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=25)

        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            group_by="column",
            auto_adjust=False,
            threads=False,
        )

        if df.empty:
            logging.warning(f"No data returned for {ticker}")
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        required = ["Open", "High", "Low", "Close", "Volume"]
        for col in required:
            if col not in df.columns:
                logging.error(f"{ticker} missing column: {col}")
                return pd.DataFrame()

        df = df[required].dropna().tail(10)
        df.reset_index(inplace=True)

        logging.info(f"Data fetched successfully for {ticker}")
        return df

    except Exception as e:
        logging.error(f"Fetch error {ticker}: {e}", exc_info=True)
        return pd.DataFrame()