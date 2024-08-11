import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import itertools
from harmonic_pattern import *
from semiBacktest import TradingStrategy  # Ensure this is the correct path

# Load pre-processed data
data = pd.read_csv("CurrencyData/preprocessed_data3.csv")
price = data["Close"]
ERROR_ALLOWED = 10.0 / 100

# Define parameter ranges
parameters = {
    'leverage_values': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    'account_risk_pct_values': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5],
    'take_profit_percent_values': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
    'stop_loss_percent_values': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
    'order': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}

parameter_combinations = list(itertools.product(*parameters.values()))

best_combination = None
max_return = -np.inf

# Assuming a vectorized approach for pattern detection (conceptual)
# Actual implementation depends heavily on pattern detection logic
def detect_patterns(price, order):
    # Placeholder for pattern detection logic
    # This function should return a DataFrame or Series indicating trade signals (buy/sell)
    return pd.Series(dtype='int')

# Example wrapper for TradingStrategy to handle vectorized signals
class VectorizedTradingStrategy:
    def __init__(self, initial_capital, leverage, account_risk_pct, take_profit_percent, stop_loss_percent, slippage_points):
        self.strategy = TradingStrategy(
            initial_capital=initial_capital,
            leverage=leverage,
            account_risk_pct=account_risk_pct,
            take_profit_percent=take_profit_percent,
            stop_loss_percent=stop_loss_percent,
            slippage_points=slippage_points
        )
        # Additional initialization as needed

    def apply_strategy(self, signals):
        # Apply strategy based on vectorized signals
        # Placeholder for trading logic application
        # This should iterate over signals and make trades accordingly
        pass

    def final_capital(self):
        # Return final capital after applying strategy
        return self.strategy.capital

# Example of iterating over parameters and applying strategy
for combination in parameter_combinations:
    strategy = VectorizedTradingStrategy(
        initial_capital=100,
        leverage=combination[0],
        account_risk_pct=combination[1],
        take_profit_percent=combination[2],
        stop_loss_percent=combination[3],
        slippage_points=2
    )
    signals = detect_patterns(price, combination[4])  # Placeholder for actual pattern detection
    strategy.apply_strategy(signals)
    final_capital = strategy.final_capital()

    if final_capital > max_return:
        max_return = final_capital
        best_combination = combination

# Output best combination and return
print(f"Best parameters: {best_combination}, Max return: {max_return}")
