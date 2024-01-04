from binance.client import Client
import pandas as pd

from scipy import stats
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
dotenv_path = "Training/.env"
load_dotenv(dotenv_path=dotenv_path)


def download():
    TRADE_SYMBOL = "ETHUSDT"

    # Binance API Client
    client = Client(os.getenv("API_KEY"), os.getenv("API_SECRET"))

    # Get all tickers
    ticker = client.get_all_tickers()
    ticker_df = pd.DataFrame(ticker)
    ticker_df = ticker_df.set_index(
        "symbol"
    )  # Set the index and assign back to ticker_df

    # Get order book
    depth = client.get_order_book(symbol=TRADE_SYMBOL)
    depth_df = pd.DataFrame(depth["bids"])
    depth_df.columns = ["Price", "Volume"]

    # Get historical klines
    historical = client.get_historical_klines(
        TRADE_SYMBOL, Client.KLINE_INTERVAL_1HOUR, "1 Jan 2011"
    )
    historical_df = pd.DataFrame(historical)
    historical_df.columns = [
        "Datetime",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Close Time",
        "Quote Asset Volume",
        "Number of Trades",
        "Taker Buy Base Asset Volume",
        "Taker Buy Quote Asset Volume",
        "Ignore",
    ]

    # Convert timestamps to datetime
    historical_df["Datetime"] = pd.to_datetime(
        historical_df["Datetime"] / 1000, unit="s"
    )
    historical_df["Close Time"] = pd.to_datetime(
        historical_df["Close Time"] / 1000, unit="s"
    )

    # Save to CSV without the index
    filename = f"CurrencyData/{TRADE_SYMBOL}.csv"
    historical_df.to_csv(filename, index=False)

    # Print first and last few rows to check
    print(historical_df.head())
    print(historical_df.tail())
    return historical_df


def preprocess_data(df):
    """
    Preprocess the data by handling duplicates, missing values, outliers, and ensuring it's sorted.

    :param df: Pandas DataFrame with historical data
    :return: Preprocessed Pandas DataFrame
    """

    # Remove any duplicate rows
    df = df.drop_duplicates()

    # Sort the data by index (datetime) just in case it's not sorted
    df.sort_index(inplace=True)

    # Convert string columns to float
    columns_to_convert = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Quote Asset Volume",
        "Number of Trades",
        "Taker Buy Base Asset Volume",
        "Taker Buy Quote Asset Volume",
    ]
    for column in columns_to_convert:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )  # Convert to float and coerce errors

    # Check for missing values (NaNs) and fill or drop them
    df.dropna(inplace=True)

    # Remove outliers
    def remove_outliers(df, column):
        z_scores = stats.zscore(df[column])
        abs_z_scores = np.abs(z_scores)
        filtered_entries = abs_z_scores < 3
        return df[filtered_entries]

    # Apply the function to the OHLC columns
    for column in columns_to_convert:
        df = remove_outliers(df, column)

    return df


if __name__ == "__main__":
    data = download()
    preprocessed_data = preprocess_data(data)
    preprocess_data(data).to_csv("CurrencyData/preprocessed_data4.csv", index=False)
