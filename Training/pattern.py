import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpdates
from mplfinance.original_flavor import candlestick_ohlc
from scipy.signal import argrelextrema
from scipy.signal import find_peaks


plt.style.use("seaborn-v0_8-darkgrid")


def load_data(filename):
    """Load CSV data into a DataFrame, parsing the 'Datetime' column as dates."""
    df = pd.read_csv(filename, parse_dates=["Datetime"])
    df.set_index("Datetime", inplace=True)
    return df


def is_downtrend(data):
    return np.all(np.diff(data) < 0)


def is_uptrend(data):
    return np.all(np.diff(data) > 0)


# def find_w_patterns(data, window_size=60, threshold=0.01):
#     w_patterns = []

#     for i in range(len(data) - window_size + 1):
#         window = data[i : i + window_size]

#         # Find local minima and maxima in the window
#         troughs = argrelextrema(window, np.less)[0]
#         peaks = argrelextrema(window, np.greater)[0]

#         # Look for the 'W' pattern in the identified troughs and peaks
#         if len(troughs) > 1 and len(peaks) > 0:
#             for j in range(1, len(troughs)):
#                 first_trough = troughs[j - 1]
#                 second_trough = troughs[j]
#                 potential_peak = peaks[(peaks > first_trough) & (peaks < second_trough)]

#                 if len(potential_peak) == 1:
#                     # Validate the 'W' pattern
#                     if (
#                         abs(window[first_trough] - window[second_trough])
#                         <= window[first_trough] * threshold
#                     ):
#                         w_patterns.append(
#                             (i + first_trough, i + potential_peak[0], i + second_trough)
#                         )
#                         break  # Stop checking if a pattern is found in this window

#     return w_patterns


def find_w_patterns(data, window_size=40, threshold=0.01):
    """
    This function finds all "W" patterns in a given data array.

    Args:
        data: A 1D NumPy array of data points.
        window_size: The size of the window to use for finding patterns.
        threshold: The maximum relative difference between the first and second troughs of the "W" pattern.

    Returns:
        A list of tuples, where each tuple represents a "W" pattern. Each tuple contains the indices of the first trough, the peak, and the second trough of the pattern.
    """

    w_patterns = []

    for i in range(len(data) - window_size + 1):
        window = data[i : i + window_size]

        # Find local minima and maxima in the window
        troughs = np.where(np.diff(np.sign(np.diff(window))) < 0)[0]
        peaks = np.where(np.diff(np.sign(np.diff(window))) > 0)[0]

        # Look for the 'W' pattern in the identified troughs and peaks
        if len(troughs) > 1 and len(peaks) > 0:
            for j in range(1, len(troughs)):
                first_trough = troughs[j - 1]
                second_trough = troughs[j]
                potential_peak = peaks[(peaks > first_trough) & (peaks < second_trough)]

                if len(potential_peak) == 1:
                    # Validate the 'W' pattern
                    if (
                        abs(window[first_trough] - window[second_trough])
                        <= window[first_trough] * threshold
                    ):
                        w_patterns.append(
                            (i + first_trough, i + potential_peak[0], i + second_trough)
                        )
                        break  # Stop checking if a pattern is found in this window

    return w_patterns


# Load data
def plot_w_patterns(df, w_patterns):
    # Convert the index to a matplotlib date format
    df["Date"] = [mpdates.date2num(d) for d in df.index]

    # Create a new figure and axis for the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot the stock data
    candlestick_ohlc(
        ax,
        df[["Date", "Open", "High", "Low", "Close"]].values,
        width=0.02,
        colorup="green",
        colordown="red",
    )

    # Highlight 'W' patterns
    for pattern in w_patterns:
        w_points = df.iloc[list(pattern)]
        ax.plot(
            w_points["Date"], w_points["Low"], marker="o", color="blue", markersize=7
        )

    # Set plot title and labels
    ax.set_title("Stock Price with Highlighted W Patterns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")

    # Format the x-axis for dates
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mpdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)

    # Show the plot
    plt.show()


# Load data
df = load_data("CurrencyData/preprocessed_data.csv")

# Find 'W' patterns
w_patterns = find_w_patterns(df["Low"].values)

# print(f"Detected patterns: {w_patterns}")

# Plot 'W' patterns
plot_w_patterns(df, w_patterns)
