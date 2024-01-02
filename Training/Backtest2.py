import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpdates
from mplfinance.original_flavor import candlestick_ohlc
from scipy.signal import argrelextrema
from scipy.signal import find_peaks
import matplotlib.dates as mdates
from tqdm import tqdm


from harmonic_pattern import *

# Load Pre-processed data
data = pd.read_csv("CurrencyData/preprocessed_data.csv")


price = data["Close"]


ERROR_ALLOWED = 10.0 / 100


order = 4
"""
max_idx = argrelextrema(price.values, np.greater, order=order)[0]  # Maxima extrema
min_idx = argrelextrema(price.values, np.less, order=order)[0]  # Minima extrema

# Merge extrema and sort
idx = list(max_idx) + list(min_idx)

idx.sort()

peaks = price.values[idx]
plt.plot(price.values)
plt.scatter(idx, peaks, c="b")
plt.plot(idx, peaks, c="r")
plt.title(f"Peaks and Troughs order={order}")
plt.show()
"""


# Initialize the plot

pnl = []
trade_dates = []
correct_pats = 0
pats = 0
fig, ax = plt.subplots()
(line,) = ax.plot([], [])  # Initialize an empty line on the plot
plt.show(block=False)


def walk_forward(price, sign, slippage=4, stop=10):
    slippage = float(slippage) / float(10000)
    stop_amount = float(stop) / float(10000)

    if sign == 1:
        initial_stop_loss = price[0] - stop_amount

        stop_loss = initial_stop_loss

        for i in range(1, len(price)):
            move = price[i] - price[i - 1]
            # For trailing stop
            if move > 0 and (price[i] - stop_amount) > initial_stop_loss:
                stop_loss = price[i] - stop_amount
            elif price[i] < stop_loss:
                return stop_loss - price[0] - slippage

    elif sign == -1:
        initial_stop_loss = price[0] + stop_amount

        stop_loss = initial_stop_loss

        for i in range(1, len(price)):
            move = price[i] - price[i - 1]
            # For trailing stop
            if move < 0 and (price[i] + stop_amount) < initial_stop_loss:
                stop_loss = price[i] + stop_amount
            elif price[i] > stop_loss:
                return price[0] - stop_loss - slippage


# Function to update plot
def update_plot(ax, line, i, cumulative_pips, order):
    line.set_xdata(np.append(line.get_xdata(), i))  # Update x-axis data
    line.set_ydata(cumulative_pips)  # Update y-axis data
    ax.relim()  # Recompute data limits
    ax.autoscale_view()  # Autoscale view based on new data limits
    accuracy = (correct_pats / pats) * 100 if pats > 0 else 0  # Calculate accuracy
    ax.set_title(
        f"Accuracy: {accuracy:.2f}% with order = {order}"
    )  # Update title with accuracy
    plt.draw()  # Redraw the figure
    plt.pause(0.05)  # Pause to allow the figure to catch up


for i in tqdm(range(order, len(price.values))):
    # print(f"values : {price.values[:i]} with I : {i}")
    print(f"LENGTH -> {order}")
    # Find maximum and minimum extrema
    max_idx = argrelextrema(price.values[:i], np.greater, order=order)[
        0
    ]  # Maxima extrema

    min_idx = argrelextrema(price.values[:i], np.less, order=order)[0]  # Minima extrema
    print(f"Maxima Indices: {max_idx}, Minima Indices: {min_idx}")
    # Merge extrema and sort
    idx = list(max_idx) + list(min_idx) + [len(price.values[:i]) - 1]

    idx.sort()
    # print(f">>>>>>  IDX ->  {idx}")

    current_idx = idx[-5:]

    if len(current_idx) < 5:
        # print(f">>>>>>  CURRENT_IDX INSIDE IF ->  {current_idx}")
        continue

    # print("CAT")
    start = min(current_idx)
    end = max(current_idx)

    # Get peaks and troughs in the extrema values
    current_pattern = price.values[current_idx]

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
    # pattern_cypher = is_cypher_pattern(LINES, ERROR_ALLOWED)

    harmonics = np.array(
        [
            pattern_gartley,
            pattern_butterfly,
            pattern_bat,
            pattern_crab,
            # pattern_shark,
            # pattern_cypher,
        ]
    )

    labels = ["Gartley", "Butterfly", "Bat", "Crab", "Shark", "Cypher"]

    if np.any(harmonics == 1) or np.any(harmonics == -1):
        for j in range(0, len(harmonics)):
            if (harmonics[j] == 1) or (harmonics[j] == -1):
                pats += 1

                sense = "Bullish" if harmonics[j] == 1 else "Bearish"
                label = sense + " " + labels[j] + " Pattern"

                begin = np.array(current_idx).min()
                finish = np.array(current_idx).max()

                date = data.iloc[end].name
                trade_dates = np.append(trade_dates, date)

                pips = walk_forward(
                    price.values[finish:], harmonics[j], slippage=4, stop=5
                )

                if pips is not None:  # Check if 'pips' is not None
                    # Update pnl list and calculate cumulative pips
                    pnl = np.append(pnl, pips)
                    print(f"PNL: {pips},{pnl}")
                    cumulative_pips = pnl.cumsum()

                    if pips > 0:  # Update the number of correct patterns detected
                        correct_pats += 1

                    # Update plot with the latest data
                    update_plot(ax, line, i, cumulative_pips, order)


plt.show()
