import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from harmonic_pattern import *
from testSlippage import TradingStrategy  # This should be your TradingStrategy class
import cma
import contextlib
import os
import random

# Load pre-processed data (ensure the CSV path is correct)
data = pd.read_csv("CurrencyData/preprocessed_data3.csv")
price = data["Close"]
ERROR_ALLOWED = 10.0 / 100

leverage_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
account_risk_pct_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
take_profit_percent_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
stop_loss_percent_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
order_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Initialize best combination tracking variables
best_combination = None
max_return = -np.inf  # A very small number since we're maximizing

# Define the number of random search iterations
num_searches = 1000  # or another number you prefer


def evaluate_strategy(combination):
    (
        leverage,
        account_risk_pct,
        take_profit_percent,
        stop_loss_percent,
        order,
    ) = combination
    leverage = int(leverage)
    account_risk_pct /= 100.0  # Convert percent to proportion
    take_profit_percent /= 100.0
    stop_loss_percent /= 100.0
    order = max(1, int(order))

    strategy = TradingStrategy(
        initial_capital=100,
        leverage=leverage,
        account_risk_pct=account_risk_pct,
        take_profit_percent=take_profit_percent,
        stop_loss_percent=stop_loss_percent,
        slippage_points=2,
    )

    # Redirect print output to null to suppress output
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        for i in range(order, len(data) - 1):
            current_price = data["Close"].iloc[i]

            # Check for new trading signals only if there is no open position
            if strategy.position == 0:
                max_idx = argrelextrema(price.values[:i], np.greater, order=order)[0]
                min_idx = argrelextrema(price.values[:i], np.less, order=order)[0]

                idx = np.concatenate((max_idx, min_idx, [i - 1]))
                idx.sort()

                current_idx = idx[-5:]
                if len(current_idx) < 5:
                    continue

                current_pattern = price.iloc[current_idx].reset_index(drop=True)
                XA = current_pattern[1] - current_pattern[0]
                AB = current_pattern[2] - current_pattern[1]
                BC = current_pattern[3] - current_pattern[2]
                CD = current_pattern[4] - current_pattern[3]
                LINES = [XA, AB, BC, CD]

                pattern_gartley = is_gartley_pattern(LINES, ERROR_ALLOWED)
                pattern_butterfly = is_butterfly_pattern(LINES, ERROR_ALLOWED)
                pattern_bat = is_bat_pattern(LINES, ERROR_ALLOWED)
                pattern_crab = is_crab_pattern(LINES, ERROR_ALLOWED)

                harmonics = np.array(
                    [pattern_gartley, pattern_butterfly, pattern_bat, pattern_crab]
                )

                if np.any(harmonics == 1):
                    strategy.execute_trade(
                        1,
                        current_price,
                        i,
                    )
                    print("Buy")
                elif np.any(harmonics == -1):
                    strategy.execute_trade(
                        -1,
                        current_price,
                        i,
                    )
                    print("Sell")

            # If there is an open position, manage the trade
            elif strategy.position != 0:
                latest_close = data["Close"].iloc[i]
                strategy.manage_open_trade(latest_close, i)

    return -strategy.capital  # Negate because later we will invert it back


# Perform random search
for _ in range(num_searches):
    current_combination = (
        random.choice(leverage_values),
        random.choice(account_risk_pct_values),
        random.choice(take_profit_percent_values),
        random.choice(stop_loss_percent_values),
        random.choice(order_values),
    )
    current_return = evaluate_strategy(current_combination)
    # Check if the current combination is better than the best one found
    if current_return > max_return:
        max_return = current_return
        best_combination = current_combination

# Convert return to positive for maximization
max_return = -max_return

print("Best parameters for max capital return:", best_combination)
print("Max capital return achieved:", max_return)

# Write the results to a file
with open("OptimizationResult_RandomSearch.txt", "w") as file:
    file.write(f"Best parameters for max capital return: {best_combination}\n")
    file.write(f"Max capital return achieved: {max_return}\n")
