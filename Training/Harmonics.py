import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpdates
from mplfinance.original_flavor import candlestick_ohlc
from scipy.signal import argrelextrema
from scipy.signal import find_peaks
import matplotlib.dates as mdates
import mplfinance as mpf

from harmonic_pattern import *

# Load Pre-processed data
data = pd.read_csv("CurrencyData/preprocessed_data.csv")


data["Datetime"] = pd.to_datetime(data["Datetime"])
data.set_index("Datetime", inplace=True)
price = data["Close"]


ERROR_ALLOWED = 10.0 / 100


order = 4


pnl = []
trade_dates = []
count = 0


for i in range(order, len(price)):
    #     # Find maximum and minimum extrema
    max_idx = argrelextrema(price.values[:i], np.greater, order=order)[
        0
    ]  # Maxima extrema
    min_idx = argrelextrema(price.values[:i], np.less, order=order)[0]  # Minima extrema

    # Merge extrema and sort
    idx = list(max_idx) + list(min_idx) + [len(price.values[:i]) - 1]

    idx.sort()

    current_idx = idx[-5:]

    # # Ensure there are enough points for the pattern
    if len(current_idx) < 5:
        continue

    start = min(current_idx)
    end = max(current_idx)

    # # Get peaks and troughs in the extrema values
    current_pattern = price.values[current_idx]
    # Get the datetime values for the pattern
    pattern_datetimes = data.index[current_idx]

    # Check for Pattern Validity
    XA = current_pattern[1] - current_pattern[0]
    AB = current_pattern[2] - current_pattern[1]
    BC = current_pattern[3] - current_pattern[2]
    CD = current_pattern[4] - current_pattern[3]

    LINES = [XA, AB, BC, CD]

    pattern_gartley = is_gartley_pattern(LINES, ERROR_ALLOWED)
    pattern_butterfly = is_butterfly_pattern(LINES, ERROR_ALLOWED)
    pattern_bat = is_bat_pattern(LINES, ERROR_ALLOWED)
    pattern_crab = is_crab_pattern(LINES, ERROR_ALLOWED)

    # pattern_shark = is_shark_pattern(LINES, ERROR_ALLOWED)
    pattern_cypher = is_cypher_pattern(LINES, ERROR_ALLOWED)

    harmonics = np.array(
        [
            pattern_gartley,
            pattern_butterfly,
            pattern_bat,
            pattern_crab,
            # pattern_shark,
            pattern_cypher,
        ]
    )

    labels = ["Gartley", "Butterfly", "Bat", "Crab", "Shark", "Cypher"]
    """
    if pattern_butterfly == 1:
        count += 1
        print(f"Count: {count}")
        print("Bullish Butterfly Pattern")
        fig, ax = plt.subplots()

        plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        plt.plot(current_idx, current_pattern, c="r")
    
        plt.title(f"Peaks and Troughs order={order}")

        plt.show()

    elif pattern_butterfly == -1:
        count += 1
        print(f"Count: {count}")
        print("Bearish Butterfly Pattern")
        plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        plt.plot(current_idx, current_pattern, c="r")

        plt.title(f"Peaks and Troughs order={order}")
        plt.show()

    elif pattern_bat == 1:
        count += 1
        print(f"Count: {count}")
        print("Bullish Bat Pattern")
        plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        plt.plot(current_idx, current_pattern, c="b")
        plt.title(f"Peaks and Troughs order={order}")
        plt.show()

    elif pattern_bat == -1:
        count += 1
        print(f"Count: {count}")
        print("Bearish Bat Pattern")
        plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        plt.plot(current_idx, current_pattern, c="b")
        plt.title(f"Peaks and Troughs order={order}")
        plt.show()

    elif pattern_crab == 1:
        count += 1
        print(f"Count: {count}")
        print("Bullish Crab Pattern")
        plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        plt.plot(current_idx, current_pattern, c="y")
        plt.title(f"Peaks and Troughs order={order}")
        plt.show()

    elif pattern_crab == -1:
        count += 1
        print(f"Count: {count}")
        print("Bearish Crab Pattern")
        plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        plt.plot(current_idx, current_pattern, c="y")
        plt.title(f"Peaks and Troughs order={order}")
        plt.show()

    elif pattern_cypher == 1:
        count += 1
        print(f"Count: {count}")
        print("Bullish Cypher Pattern")
        plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        plt.plot(current_idx, current_pattern, c="m")
        plt.title(f"Peaks and Troughs order={order}")
        plt.show()

    elif pattern_cypher == -1:
        count += 1
        print(f"Count: {count}")
        print("Bearish Cypher Pattern")
        plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        plt.plot(current_idx, current_pattern, c="m")
        plt.title(f"Peaks and Troughs order={order}")
        plt.show()

    """

    if pattern_butterfly == 1:
        print("Bullish Butterfly Pattern")

        plt.plot(data.index[start : i + 20], price[start : i + 20])
        plt.plot(
            pattern_datetimes, current_pattern, color="red", label="Pattern Points"
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.show()

        # plt.plot(np.arange(start, i + 20), price.values[start : i + 20])
        # plt.plot(current_idx, current_pattern, c="r")
        # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        # plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        # plt.gcf().autofmt_xdate()

        # plt.title(f"Peaks and Troughs order={order}")

        # plt.show()

    elif pattern_butterfly == -1:
        print("Bearish Butterfly Pattern")
        plt.plot(data.index[start : i + 20], price[start : i + 20])
        plt.plot(
            pattern_datetimes, current_pattern, color="red", label="Pattern Points"
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.show()

    elif pattern_bat == 1:
        print("Bullish Bat Pattern")
        plt.plot(data.index[start : i + 20], price[start : i + 20])
        plt.plot(
            pattern_datetimes, current_pattern, color="blue", label="Pattern Points"
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.show()

    elif pattern_bat == -1:
        print("Bearish Bat Pattern")
        plt.plot(data.index[start : i + 20], price[start : i + 20])
        plt.plot(
            pattern_datetimes, current_pattern, color="blue", label="Pattern Points"
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.show()

    elif pattern_crab == 1:
        print("Bullish Crab Pattern")
        plt.plot(data.index[start : i + 20], price[start : i + 20])
        plt.plot(
            pattern_datetimes, current_pattern, color="orange", label="Pattern Points"
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.show()
    elif pattern_crab == -1:
        print("Bearish Crab Pattern")
        plt.plot(data.index[start : i + 20], price[start : i + 20])
        plt.plot(
            pattern_datetimes, current_pattern, color="orange", label="Pattern Points"
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.show()

    elif pattern_cypher == 1:
        print("Bullish Cypher Pattern")
        plt.plot(data.index[start : i + 20], price[start : i + 20])
        plt.plot(pattern_datetimes, current_pattern, color="m")

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.show()

    elif pattern_cypher == -1:
        print("Bearish Cypher Pattern")
        plt.plot(data.index[start : i + 20], price[start : i + 20])
        plt.plot(pattern_datetimes, current_pattern, color="m")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()

        plt.show()
