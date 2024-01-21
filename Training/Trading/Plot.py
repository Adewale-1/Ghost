import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import matplotlib.dates as mdates
from harmonic_pattern import (
    is_gartley_pattern,
    is_butterfly_pattern,
    is_bat_pattern,
    is_crab_pattern,
)

# from backtest import entry, tp, sl, good_trade, bad_trade, data

from testSlippage import entry, tp, sl, good_trade, bad_trade, data


# Load Pre-processed data

data["Datetime"] = pd.to_datetime(data["Datetime"])
data.set_index("Datetime", inplace=True)
price = data["Close"]

ERROR_ALLOWED = 10.0 / 100
order = 4


entry_points = entry
take_profits = tp
stop_losses = sl
profitable_trades = good_trade
non_profitable_trades = bad_trade


# Making sure we have trades to plot
if entry_points:
    entry_indices = [ep[0] for ep in entry_points]
    entry_datetimes = data.index[entry_indices].tolist()
    entry_prices = [ep[1] for ep in entry_points]

    tp_datetimes = data.index[[tp[0] for tp in take_profits]].tolist()
    tp_prices = [tp[1] for tp in take_profits]

    sl_datetimes = data.index[[sl[0] for sl in stop_losses]].tolist()
    sl_prices = [sl[1] for sl in stop_losses]

    profitable_datetimes = data.index[[pt[0] for pt in profitable_trades]].tolist()
    profitable_prices = [pt[1] for pt in profitable_trades]

    non_profitable_datetimes = data.index[
        [npt[0] for npt in non_profitable_trades]
    ].tolist()
    non_profitable_prices = [npt[1] for npt in non_profitable_trades]

    # Plotting the close prices
    plt.figure(figsize=(15, 9))
    plt.plot(data.index, data["Close"], label="Close Price", color="blue", linewidth=1)

    plt.scatter(
        data.index[[ep[0] for ep in entry_points]],
        [ep[1] for ep in entry_points],
        color="green",
        marker="^",
        label="Entry Points",
    )

    plt.scatter(
        data.index[[tp[0] for tp in take_profits]],
        [tp[1] for tp in take_profits],
        color="gold",
        marker="*",
        label="Take Profit Levels",
    )

    plt.scatter(
        data.index[[sl[0] for sl in stop_losses]],
        [sl[1] for sl in stop_losses],
        color="red",
        marker="v",
        label="Stop Loss Levels",
    )

    plt.scatter(
        data.index[[pt[0] for pt in profitable_trades]],
        [pt[1] for pt in profitable_trades],
        color="lightgreen",
        marker="o",
        label="Profitable Trades",
    )

    plt.scatter(
        data.index[[npt[0] for npt in non_profitable_trades]],
        [npt[1] for npt in non_profitable_trades],
        color="pink",
        marker="x",
        label="Non-profitable Trades",
    )

    # Detect and plot harmonic patterns
    for i in range(order, len(data["Close"]) + 1):
        relevant_data = data["Close"].iloc[i - order : i]
        max_idx = argrelextrema(relevant_data.values, np.greater, order=1)[0]
        min_idx = argrelextrema(relevant_data.values, np.less, order=1)[0]
        idx = np.sort(np.concatenate((max_idx, min_idx)))

        # Include only last five points to define a potential pattern
        if len(idx) >= 5:
            pattern_prices = relevant_data.values[idx[-5:]]
            XA = pattern_prices[1] - pattern_prices[0]
            AB = pattern_prices[2] - pattern_prices[1]
            BC = pattern_prices[3] - pattern_prices[2]
            CD = pattern_prices[4] - pattern_prices[3]
            LINES = [XA, AB, BC, CD]

            if is_gartley_pattern(LINES, ERROR_ALLOWED):
                plt.plot(
                    relevant_data.index[idx[-5:]],
                    pattern_prices,
                    "r-",
                    label="Gartley Pattern",
                )
            if is_butterfly_pattern(LINES, ERROR_ALLOWED):
                plt.plot(
                    relevant_data.index[idx[-5:]],
                    pattern_prices,
                    "g-",
                    label="Butterfly Pattern",
                )
            if is_bat_pattern(LINES, ERROR_ALLOWED):
                plt.plot(
                    relevant_data.index[idx[-5:]],
                    pattern_prices,
                    "b-",
                    label="Bat Pattern",
                )
            if is_crab_pattern(LINES, ERROR_ALLOWED):
                plt.plot(
                    relevant_data.index[idx[-5:]],
                    pattern_prices,
                    "y-",
                    label="Crab Pattern",
                )

    # Avoid duplicate labels in the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    unique = [
        (h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]
    ]
    plt.legend(*zip(*unique))

    # Formatting dates on the x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

    # Rotating date labels
    plt.gcf().autofmt_xdate()

    plt.title("Backtesting Trade Visualization")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("No trades executed.")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gcf().autofmt_xdate()  # rotate and align the tick labels
plt.title("Price Chart with Harmonic Patterns")
plt.xlabel("Date")
plt.ylabel("Price")

plt.show()
