import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import random

import random
from harmonic_pattern import *

# Load pre-processed data
data = pd.read_csv("CurrencyData/preprocessed_data.csv")
price = data["Close"]

ERROR_ALLOWED = 10.0 / 100
order = 4

"""
For order 1 ;
    Profitable paercentage: 40.35%
For order 2 ;
    Profitable paercentage: 42.0%
For order 3 ;
    Profitable paercentage: 42.5%
For order 4 ;
    Profitable paercentage:  43.95%
For order 5 ;
    Profitable paercentage: 35.0%
For order 7 ;
    Profitable paercentage: 38.0%

"""


class TradingStrategy:
    def __init__(self, initial_capital, position_size, slippage_points):
        self.capital = initial_capital
        self.position_size = position_size
        self.slippage_points = slippage_points
        self.position = 0  # 1 for long, -1 for short, 0 for no position
        self.entry_price = 0
        self.trade_results = []
        self.entry_points = []
        self.take_profits = []
        self.stop_losses = []
        self.profitable_trades = []
        self.non_profitable_trades = []

    def walk_forward_on_data(
        self, prices_df, sign, slippage_percent=0.02, stop_loss_percent=0.01
    ):
        self.entry_price = prices_df["Close"].iloc[0]

        # Calculate slippage and stop-loss amount as percentages of the entry price
        slippage_amount = self.entry_price * slippage_percent
        stop_amount = self.entry_price * stop_loss_percent

        # Initialize the stop-loss based on the position's sign
        initial_stop_loss = (
            self.entry_price - stop_amount if sign == 1 else self.entry_price + stop_amount
        )
        stop_loss = initial_stop_loss

        for i in range(1, len(prices_df)):
            if sign == 1:
                if prices_df["Close"].iloc[i] > stop_loss + stop_amount:
                    stop_loss = prices_df["Close"].iloc[i] - stop_amount

                if prices_df["Close"].iloc[i] < stop_loss:
                    exit_price = (
                        max(prices_df["Open"].iloc[i], stop_loss) - slippage_amount
                    )
                    pnl = exit_price - self.entry_price
                    return pnl

            # Update stop-loss logic for short position
            elif sign == -1:
                if prices_df["Close"].iloc[i] < stop_loss - stop_amount:
                    stop_loss = prices_df["Close"].iloc[i] + stop_amount

                if prices_df["Close"].iloc[i] > stop_loss:
                    exit_price = (
                        min(prices_df["Open"].iloc[i], stop_loss) + slippage_amount
                    )
                    pnl = self.entry_price - exit_price
                    return pnl

        return None

    def execute_trade(
        self, trade_signal, current_price, i, risk_percent=0.01, tp_percent=0.02
    ):
        if trade_signal != 0 and self.position == 0:  # Only enter if no open position
            self.position = trade_signal

            # Calculate entry price with realistic slippage
            # Simulate variable slippage by choosing a random value within a range
            slippage_range = (
                1,
                5,
            )  # Define a tuple representing the slippage range in points (multiply by 0.0001 for the value)
            random_slippage_points = random.randint(*slippage_range) / 10000

            if trade_signal == 1:
                entry_price_adjustment = random_slippage_points
            else:
                entry_price_adjustment = -random_slippage_points
            self.entry_price = current_price + entry_price_adjustment

            self.entry_points.append((i, self.entry_price))  # Record entry

            # Calculate take profit and stop loss levels based on 1:2 risk-reward ratio
            if trade_signal == 1:
                tp_adjustment = tp_percent
            else:
                tp_adjustment = -tp_percent

            sl_adjustment = -risk_percent if trade_signal == 1 else risk_percent
            tp_price = self.entry_price * (1 + tp_adjustment)
            sl_price = self.entry_price * (1 + sl_adjustment)

            self.take_profits.append((i, tp_price))
            self.stop_losses.append((i, sl_price))

            print(
                f"New trade at index {i}: {'Buy' if trade_signal == 1 else 'Sell'} at {self.entry_price}, TP: {tp_price}, SL: {sl_price}"
            )

    def manage_open_trade(self, latest_close, i):
        if self.position != 0:
            existing_trade_index = self.entry_points[-1][0]
            existing_entry_price = self.entry_points[-1][1]
            existing_tp_price = self.take_profits[-1][1]
            existing_sl_price = self.stop_losses[-1][1]

            # Apply slippage on exit price
            exit_slippage = self.slippage_points * 0.0001

        # Check if either the stop loss or take profit levels are hit
        if self.position == 1:  # For a long position
            if latest_close >= existing_tp_price:
                exit_price = existing_tp_price - exit_slippage  # Apply slippage
                pnl = (exit_price - existing_entry_price) * self.position_size
            elif latest_close <= existing_sl_price:
                exit_price = existing_sl_price + exit_slippage  # Apply slippage
                pnl = (exit_price - existing_entry_price) * self.position_size

            # If trade is closed, reset the position and update capital
            if latest_close >= existing_tp_price or latest_close <= existing_sl_price:
                self.capital += pnl
                self.trade_results.append(pnl)
                if pnl > 0:
                    self.profitable_trades.append((existing_trade_index, exit_price))
                else:
                    self.non_profitable_trades.append(
                        (existing_trade_index, exit_price)
                    )
                self.position = 0
                print(f"Long trade closed at index {i} with PnL: {pnl}")

        elif self.position == -1:  # For a short position
            if latest_close <= existing_tp_price:
                exit_price = existing_tp_price + exit_slippage  # Apply slippage
                pnl = (existing_entry_price - exit_price) * self.position_size
            elif latest_close >= existing_sl_price:
                exit_price = existing_sl_price - exit_slippage  # Apply slippage
                pnl = (existing_entry_price - exit_price) * self.position_size

            # If trade is closed, reset the position and update capital
            if latest_close <= existing_tp_price or latest_close >= existing_sl_price:
                self.capital += pnl
                self.trade_results.append(pnl)
                if pnl > 0:
                    self.profitable_trades.append((existing_trade_index, exit_price))
                else:
                    self.non_profitable_trades.append(
                        (existing_trade_index, exit_price)
                    )
                self.position = 0
                print(f"Short trade closed at index {i} with PnL: {pnl}")


"""
    Create the strategy object
"""
strategy = TradingStrategy(initial_capital=100, position_size=1, slippage_points=2)
"""
    Main backtesting loop
"""
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
                1, current_price, i, risk_percent=0.01, tp_percent=0.02
            )
        elif np.any(harmonics == -1):
            strategy.execute_trade(
                -1, current_price, i, risk_percent=0.01, tp_percent=0.02
            )

    # If there is an open position, manage the trade
    elif strategy.position != 0:
        latest_close = data["Close"].iloc[i]
        strategy.manage_open_trade(latest_close, i)


# Sum up the profits and losses from all trades
total_pnl = sum(strategy.trade_results)

# Calculate the unrealized profit/loss for any open position
unrealized_pnl = 0
if strategy.position != 0:
    latest_close = data["Close"].iloc[-1]  # Get the latest closing price
    if strategy.position == 1:  # Long position
        unrealized_pnl = (latest_close - strategy.entry_price) * strategy.position_size
    elif strategy.position == -1:  # Short position
        unrealized_pnl = (strategy.entry_price - latest_close) * strategy.position_size

# Final capital is initial capital plus total realized pnl and unrealized pnl
final_capital = strategy.capital + unrealized_pnl

print(f"Final Capital: {final_capital}")
print(f"Trade Results: {strategy.trade_results}")
print(f"Entry Points: {strategy.entry_points}")
print(f"Take Profits: {strategy.take_profits}")
print(f"Stop Losses: {strategy.stop_losses}")
print(f"Profitable Trades: {strategy.profitable_trades}")
print(f"Non-Profitable Trades: {strategy.non_profitable_trades}")
print(f"Total Trades: {len(strategy.entry_points)}")
print(f"Total number of profitable trades: {len(strategy.profitable_trades)}")
print(f"Total number of non-profitable trades: {len(strategy.non_profitable_trades)}")
print(f"Order: {order}")
print(
    f"Percentage of Profitable Trades: {(100 * len(strategy.profitable_trades))/len(strategy.entry_points)}%"
)


"""
    Plotting the close prices
"""
entry = strategy.entry_points
tp = strategy.take_profits
sl = strategy.stop_losses
good_trade = strategy.profitable_trades
bad_trade = strategy.non_profitable_trades
