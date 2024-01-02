import pandas as pd
from scipy import stats

from data_collector import *


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

    # Check for missing values (NaNs) and fill or drop them
    if df.isnull().values.any():
        # Option 1: Fill missing values, for example with the previous value
        df.fillna(method="ffill", inplace=True)
        # Option 2: Drop rows with missing values
        # df.dropna(inplace=True)

    # Remove outliers
    # Define a function to remove outliers based on Z-score
    def remove_outliers(df, column):
        return df[(abs(stats.zscore(df[column])) < 3)]

    # Apply the function to the OHLC columns
    columns_to_check = ["Open", "High", "Low", "Close"]
    for column in columns_to_check:
        df = remove_outliers(df, column)

    return df


if __name__ == "__main__":
    currency_pair = input("Enter currency pair: ")
    start_date = input("Enter start date (YYYY-MM-DD): ")
    time_interval = input("Enter time interval: ")

    # Get the current date as the end date
    end_date = datetime.now().strftime("%Y-%m-%d")

    data = download_data(currency_pair, start_date, end_date, time_interval)

    # Assuming you have already downloaded the data and have it in a DataFrame `data`
    # Apply the preprocessing function to the data
    preprocessed_data = preprocess_data(data)
    preprocess_data(data).to_csv("CurrencyData/preprocessed_data2.csv")
