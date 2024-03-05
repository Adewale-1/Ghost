import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import itertools
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harmonic_pattern import *
from testSlippage import TradingStrategy
import multiprocessing

def evaluate_combination(combination, data_path, error_allowed):
    # Load data inside the function to ensure each process has its own copy
    data = pd.read_csv(data_path)
    price = data["Close"]
    
    leverage, account_risk_pct, take_profit_percent, stop_loss_percent, order = combination
    strategy = TradingStrategy(
        initial_capital=100,
        leverage=leverage,
        account_risk_pct=account_risk_pct,
        take_profit_percent=take_profit_percent,
        stop_loss_percent=stop_loss_percent,
        slippage_points=2,
    )

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

            pattern_gartley = is_gartley_pattern(LINES, error_allowed)
            pattern_butterfly = is_butterfly_pattern(LINES, error_allowed)
            pattern_bat = is_bat_pattern(LINES, error_allowed)
            pattern_crab = is_crab_pattern(LINES, error_allowed)

            harmonics = np.array(
                [pattern_gartley, pattern_butterfly, pattern_bat, pattern_crab]
            )

            if np.any(harmonics == 1):
                strategy.execute_trade(
                    1,
                    current_price,
                    i,
                )
            elif np.any(harmonics == -1):
                strategy.execute_trade(
                    -1,
                    current_price,
                    i,
                )

        # If there is an open position, manage the trade
        elif strategy.position != 0:
            latest_close = data["Close"].iloc[i]
            strategy.manage_open_trade(latest_close, i)
        
    final_capital = strategy.capital
    return final_capital, combination

if __name__ == "__main__":
    data_path = "CurrencyData1/preprocessed_data3.csv"
    error_allowed = 10.0 / 100
    
    # Define parameter ranges
    leverage_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    account_risk_pct_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
    take_profit_percent_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    stop_loss_percent_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Create a Cartesian product of all parameter combinations
    parameter_combinations = list(
        itertools.product(
            leverage_values,
            account_risk_pct_values,
            take_profit_percent_values,
            stop_loss_percent_values,
            order,
        )
    )

     # Number of processes
    num_processes = multiprocessing.cpu_count()

    # Create a pool of processes
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Map the evaluate_combination function to each combination
        results = pool.starmap(evaluate_combination, [(combination, data_path, error_allowed) for combination in parameter_combinations])

    # Find the best combination from the results
    max_return, best_combination = max(results, key=lambda x: x[0])
    # Write the best parameter combination to a text file
    with open("OptimizationMulti-CoreResult.txt", "w") as file:
        file.write(
            f"Maximum capital return: {max_return}\n"
            f"Best parameters for max capital return: Leverage: {best_combination[0]},\n"
            f"Account Risk%: {best_combination[1]},\n Take Profit%: {best_combination[2]},\n"
            f"Stop Loss%: {best_combination[3]},\n Best order: {best_combination[4]}"
        )

    # Print the best parameter combination (Leverage, Account Risk%, Take Profit%, Stop Loss%)
    print(
        f"Best parameters for max capital return: Leverage: {best_combination[0]}, "
        f"Account Risk%: {best_combination[1]}, Take Profit%: {best_combination[2]}, "
        f"Stop Loss%: {best_combination[3]},Best order: {best_combination[4]}"
    )
    print(f"Max capital return: {max_return}")