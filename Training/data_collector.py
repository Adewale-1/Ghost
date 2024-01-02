import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
import time
import logging

# Set up basic logging
logging.basicConfig(
    filename="data_collector.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def download_data(currency_pair, start_date, end_date, time_interval, retries=3):
    """
    Downloads historical data for a given currency pair and time interval with retry mechanism.

    :param currency_pair: String in the format 'EURUSD=X'
    :param start_date: String in the format 'YYYY-MM-DD'
    :param end_date: String in the format 'YYYY-MM-DD'
    :param time_interval: String, valid intervals: '1m', '2m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'
    :param retries: Int, number of retries for downloading data in case of failure
    :return: A Pandas DataFrame with historical data
    """

    attempt = 0
    while attempt < retries:
        try:
            # Querying the data
            df = yf.download(
                currency_pair,
                start=start_date,
                end=end_date,
                interval=time_interval,
                progress=False,
            )

            # Check if the dataframe is empty
            if df.empty:
                raise ValueError(
                    f"No data found for {currency_pair} at {datetime.now()} using interval {time_interval}."
                )

            # Data integrity validation check (e.g., no NaN values)
            if df.isnull().values.any():
                raise ValueError("Data contains NaN values.")

            # Save the DataFrame to a CSV file in the current working directory
            filename = f"CurrencyData/{currency_pair}-{start_date}-{end_date}-{time_interval}.csv"

            df.to_csv(filename)
            logging.info(f"Data saved to {filename}")
            print(f"Data saved to {filename}")

            return df
        except ValueError as e:
            logging.error(e)
            print(e)
            break  # Stop retrying after a data-related error
        except Exception as e:
            logging.error(f"An error occurred on attempt {attempt + 1}: {e}")
            print(f"An error occurred on attempt {attempt + 1}: {e}")
            time.sleep(5)  # Wait before retrying
        attempt += 1

    logging.error(f"All {retries} download attempts failed.")
    sys.exit(f"Failed to download data after {retries} attempts. Exiting.")


# if __name__ == "__main__":
#     currency_pair = input("Enter currency pair: ")
#     start_date = input("Enter start date (YYYY-MM-DD): ")
#     time_interval = input("Enter time interval: ")

#     # Get the current date as the end date
#     end_date = datetime.now().strftime("%Y-%m-%d")

#     data = download_data(currency_pair, start_date, end_date, time_interval)
