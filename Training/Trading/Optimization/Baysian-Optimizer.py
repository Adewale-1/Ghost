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

# Load pre-processed data (ensure the CSV path is correct)
data = pd.read_csv(
    "/Users/adewaleadenle/Software Development/GitHub Projects/Ghost/Training/Trading/CurrencyData/preprocessed_data2.csv"
)
price = data["Close"]
# ERROR_ALLOWED = 10.0 / 100


def evaluate_strategy(
    leverage, account_risk_pct, take_profit_percent, stop_loss_percent, order, error_allowed
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
    return final_capital


# Wrapper function to use Bayesian optimization
def strategy_wrapper(
    leverage,
    account_risk_pct,
    take_profit_percent,
    stop_loss_percent,
    order,
    error_allowed,
):
    return evaluate_strategy(
        leverage=leverage,
        account_risk_pct=account_risk_pct,
        take_profit_percent=take_profit_percent,
        stop_loss_percent=stop_loss_percent,
        order=order,
        error_allowed=error_allowed,
    )


# Define bounds for Bayesian Optimization
bounds = {
    "leverage": (5, 20),
    "account_risk_pct": (5, 25),
    "take_profit_percent": (1, 10),
    "stop_loss_percent": (1, 10),
    "order": (1, 10),
    "error_allowed": (0.1,0.8)
}

optimizer = BayesianOptimization(
    f=strategy_wrapper,
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
