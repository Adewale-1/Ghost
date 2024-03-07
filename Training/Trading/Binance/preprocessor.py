import pandas as pd
from scipy import stats


class Preprocessor:
    def __init__(self, data):
        self.data = data

    def preprocess_data(self):
        """
        Preprocess the data by handling duplicates, missing values, outliers, and ensuring it's sorted.

        :param df: Pandas DataFrame with historical data
        :return: Preprocessed Pandas DataFrame
        """

        # Remove any duplicate rows
        df = self.data.drop_duplicates()

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