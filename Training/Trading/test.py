import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import random

import random
from harmonic_pattern import *

# Load pre-processed data
data = pd.read_csv("CurrencyData/preprocessed_data2.csv")
price = data["Close"]

ERROR_ALLOWED = 10.0 / 100
order = 1

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
    RISK_REWARD_RATIO = 2.0
    RISK = 1.0

    def __init__(self, initial_capital, leverage, account_risk_pct, slippage_points):
        self.capital = initial_capital
        self.leverage = leverage
        self.account_risk_pct = account_risk_pct
        self.slippage_points = slippage_points
        self.position = 0  # 1 for long, -1 for short, 0 for no position
        self.entry_price = 0
        self.position_size = 0
        self.trade_results = []
        self.entry_points = []
        self.take_profits = []
        self.stop_losses = []
        self.profitable_trades = []
        self.non_profitable_trades = []
        self.array = []

    def walk_forward_on_data(
        self, prices_df, sign, slippage_percent=0.02, stop_loss_percent=0.01
    ):
        self.entry_price = prices_df["Close"].iloc[0]

        # Calculate slippage and stop-loss amount as percentages of the entry price
        slippage_amount = self.entry_price * slippage_percent
        stop_amount = self.entry_price * stop_loss_percent

        # Initialize the stop-loss based on the position's sign
        initial_stop_loss = (
            self.entry_price - stop_amount
            if sign == 1
            else self.entry_price + stop_amount
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
        if trade_signal != 0 and self.position == 0:
            # Calculate the amount of capital at risk
            trade_risk = self.capital * risk_percent

            # Check if the trade risk is greater than the total capital
            if trade_risk > self.capital:
                print("Insufficient capital to execute trade.")
                return
            self.capital -= trade_risk
            self.position = trade_signal
            slippage_adjustment = self.slippage_points * 0.0001
            self.entry_price = current_price * (
                1 + slippage_adjustment
                if trade_signal == 1
                else 1 - slippage_adjustment
            )
            self.entry_points.append((i, self.entry_price))

            # Calculate the position size based on leverage, not the total capital
            self.position_size = trade_risk * self.leverage

            # Calculate take profit and stop loss prices
            tp_adjustment = tp_percent if trade_signal == 1 else -tp_percent
            sl_adjustment = -risk_percent if trade_signal == 1 else risk_percent
            tp_price = self.entry_price * (1 + tp_adjustment)
            sl_price = self.entry_price * (1 + sl_adjustment)

            self.take_profits.append((i, tp_price))
            self.stop_losses.append((i, sl_price))

            print(
                f"Trade {i}: {'Buy' if trade_signal == 1 else 'Sell'} at {self.entry_price}, Trade Risk: {trade_risk} Position Size: {self.position_size} Current Capital: {self.capital}, TP: {tp_price}, SL: {sl_price}"
            )

    def manage_open_trade(self, latest_price, i):
        if self.position != 0 and self.capital > 0:
            _, existing_trade_index = self.entry_points[-1][0]
            _, entry_price = self.entry_points[-1]
            _, tp_price = self.take_profits[-1]
            _, sl_price = self.stop_losses[-1]

            trade_closed = False
            pnl = 0

            # Calculate the PnL based on the risk-to-reward ratio
            if self.position == 1:  # Long position
                if latest_price >= tp_price:
                    pnl = self.position_size * 0.02  # 2% profit of position size
                    trade_closed = True
                elif latest_price <= sl_price:
                    pnl = -(self.position_size) * 0.01  # 1% loss of position size
                    trade_closed = True

            elif self.position == -1:  # Short position
                if latest_price <= tp_price:
                    pnl = self.position_size * 0.02  # 2% profit of position size
                    trade_closed = True
                elif latest_price >= sl_price:
                    pnl = -(self.position_size) * 0.01  # 1% loss of position size
                    trade_closed = True

            if trade_closed:
                # Re-add the risked amount and the PnL to the capital
                self.capital += (self.position_size / self.leverage) + pnl
                self.trade_results.append(pnl)
                self.position = 0  # Reset position
                self.position_size = 0  # Reset position size
                print(f"Trade {i} closed with PnL: {pnl}, Capital: {self.capital}")
        else:
            print("Out of capital, cannot trade!")


"""
    Create the strategy object
"""

strategy = TradingStrategy(
    initial_capital=100, leverage=10, account_risk_pct=0.1, slippage_points=2
)
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
                1,
                current_price,
                i,
                risk_percent=strategy.account_risk_pct,
                tp_percent=0.02,
            )
        elif np.any(harmonics == -1):
            strategy.execute_trade(
                -1,
                current_price,
                i,
                risk_percent=strategy.account_risk_pct,
                tp_percent=0.02,
            )

    # If there is an open position, manage the trade
    elif strategy.position != 0:
        latest_close = data["Close"].iloc[i]
        strategy.manage_open_trade(latest_close, i)


print(f"Final Capital: {strategy.capital}")
print(f"Total PnL from Trades: {sum(strategy.trade_results)}")
# print(f"Trade Results: {strategy.trade_results}")
# print(f"Entry Points: {strategy.entry_points}")
# print(f"Take Profits: {strategy.take_profits}")
# print(f"Stop Losses: {strategy.stop_losses}")
# print(f"Profitable Trades: {strategy.profitable_trades}")
# print(f"Non-Profitable Trades: {strategy.non_profitable_trades}")
# print(f"Total Trades: {len(strategy.entry_points)}")
# print(f"Total number of profitable trades: {len(strategy.profitable_trades)}")
# print(f"Total number of non-profitable trades: {len(strategy.non_profitable_trades)}")
print(f"Order: {order}")
# print(
#     f"Percentage of Profitable Trades: {(100 * len(strategy.profitable_trades))/len(strategy.entry_points)}%"
# )


"""
    Plotting the close prices
"""
entry = strategy.entry_points
tp = strategy.take_profits
sl = strategy.stop_losses
good_trade = strategy.profitable_trades
bad_trade = strategy.non_profitable_trades
