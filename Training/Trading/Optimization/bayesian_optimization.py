import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from bayes_opt import BayesianOptimization
import sys
import os

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from harmonic_pattern import *
from tradingStrategy import TradingStrategy
import os
import contextlib
from data_enrichment import calculate_enhanced_signals

# Load pre-processed data (ensure the CSV path is correct)
data = pd.read_csv(
    "/Users/adewaleadenle/Software Development/GitHub Projects/Ghost/Training/Trading/CurrencyData/preprocessed_data2.csv"
)
# price = data["Close"]
# ERROR_ALLOWED = 10.0 / 100


def walk_forward_analysis(
    data, window_size, step_size, optimization_func, evaluation_func
):
    results = []
    all_best_params = []
    for i in range(0, len(data) - window_size - step_size, step_size):
        train_data = data.iloc[i : i + window_size].copy()
        test_data = data.iloc[i + window_size : i + window_size + step_size].copy()

        # Optimize on train data
        optimizer = BayesianOptimization(
            f=optimization_func(train_data),
            pbounds=bounds,
            random_state=1,
        )
        optimizer.maximize(init_points=5, n_iter=25)

        # Get best parameters
        best_params = optimizer.max["params"]
        best_params["leverage"] = int(best_params["leverage"])
        best_params["order"] = int(best_params["order"])
        all_best_params.append(best_params)

        # Evaluate on test data
        test_result = evaluation_func(test_data, **best_params)
        results.append(test_result)

    return results, all_best_params


# def evaluate_strategy(data, leverage, account_risk_pct, take_profit_percent, stop_loss_percent, order, error_allowed):


def calculate_rsi(data, period=14):
    close_delta = data["Close"].diff()

    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    # Use exponential moving average
    ma_up = up.ewm(com=period - 1, adjust=True, min_periods=period).mean()
    ma_down = down.ewm(com=period - 1, adjust=True, min_periods=period).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))

    return rsi


def evaluate_strategy(
    data,
    leverage,
    account_risk_pct,
    take_profit_percent,
    stop_loss_percent,
    order,
    error_allowed,
    rsi_period,
    rsi_oversold,
    rsi_overbought,
):
    strategy = TradingStrategy(
        initial_capital=100,
        leverage=int(leverage),
        account_risk_pct=account_risk_pct / 100.00,
        take_profit_percent=take_profit_percent / 100.00,
        stop_loss_percent=stop_loss_percent / 100.00,
        slippage_points=2,
    )

    # Convert order to an integer and ensure it's 1 or more
    order = max(1, int(order))
    data = calculate_enhanced_signals(data)
    # Calculate RSI for the current data
    data.loc[:, "RSI"] = calculate_rsi(data, period=int(rsi_period))

    price = data["Close"]
    # Redirect print output to null to suppress output
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        for i in range(order, len(data) - 1):
            current_price = data["Close"].iloc[i]
            rsi = data["RSI"].iloc[i]
            tot_signal = data["TotSignal"].iloc[i]

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

                # Incorporate new signals into trading decision
                if np.any(harmonics == 1) and (rsi < rsi_oversold) and tot_signal == 1:
                    strategy.execute_trade(1, current_price, i)
                elif (
                    np.any(harmonics == -1)
                    and (rsi > rsi_overbought)
                    and tot_signal == -1
                ):
                    strategy.execute_trade(-1, current_price, i)

            # If there is an open position, manage the trade
            elif strategy.position != 0:
                latest_close = data["Close"].iloc[i]
                strategy.manage_open_trade(latest_close, i)

    final_capital = strategy.capital
    return final_capital


# Wrapper function to use Bayesian optimization
def strategy_wrapper(data):
    def wrapper(
        leverage,
        account_risk_pct,
        take_profit_percent,
        stop_loss_percent,
        order,
        error_allowed,
        rsi_period,
        rsi_oversold,
        rsi_overbought,
    ):
        return evaluate_strategy(
            data=data,
            leverage=leverage,
            account_risk_pct=account_risk_pct,
            take_profit_percent=take_profit_percent,
            stop_loss_percent=stop_loss_percent,
            order=order,
            error_allowed=error_allowed,
            rsi_period=rsi_period,
            rsi_oversold=rsi_oversold,
            rsi_overbought=rsi_overbought,
        )

    return wrapper


# Define bounds for Bayesian Optimization
bounds = {
    "leverage": (5, 20),
    "account_risk_pct": (5, 25),
    "take_profit_percent": (1, 10),
    "stop_loss_percent": (1, 10),
    "order": (1, 10),
    "error_allowed": (0.1, 0.5),
    "rsi_period": (7, 21),
    "rsi_oversold": (20, 40),
    "rsi_overbought": (60, 80),
}

optimizer = BayesianOptimization(
    f=strategy_wrapper(data),  # Pass data here
    pbounds=bounds,
    random_state=1,
)
optimizer.maximize(
    init_points=5,
    n_iter=25,
)

# Retrieve best parameters found
best_params = optimizer.max["params"]
best_params["leverage"] = int(best_params["leverage"])
best_params["order"] = int(best_params["order"])

print("Best parameters for max capital return:", best_params)
print("Max capital return achieved:", optimizer.max["target"])

# Saving results
with open("OptimizationResult_Baysian.txt", "w") as file:
    file.write(
        f"Maximum capital return: {optimizer.max['target']}\n"
        f"Best parameters for max capital return:\n {best_params}"
    )

__all__ = ["walk_forward_analysis", "evaluate_strategy", "strategy_wrapper"]
