import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import random
import random


from harmonic_pattern import *


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

    """
    Initialize the TradingStrategy object with the following parameters:
    """

    def __init__(
        self,
        initial_capital,
        leverage,
        account_risk_pct,
        take_profit_percent,
        stop_loss_percent,
        slippage_points,
    ):
        self.capital = initial_capital
        self.leverage = leverage
        self.account_risk_pct = account_risk_pct
        self.slippage_points = slippage_points
        self.position = 0  # 1 for long, -1 for short, 0 for no position
        self.entry_price = 0
        self.position_size = 0
        self.take_profit_percent = take_profit_percent
        self.stop_loss_percent = stop_loss_percent
        self.trade_results = []
        self.entry_points = []
        self.take_profits = []
        self.stop_losses = []
        self.liqudation_prices = []
        self.profitable_trades = []
        self.non_profitable_trades = []

    def walk_forward_on_Data(
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

    """
        Calculate the estimated liquidation price based on the leverage, entry price and maintenance margin
    """

    def EstimatedLiquidationPrice(
        self, trade_signal, entry_price, leverage_value, Maintenance_Margin
    ):
        liquidation_price = 0
        Initial_Margin_Rate = 1 / leverage_value
        Maintenance_Margin_Rate = Maintenance_Margin / 100
        if trade_signal == 1:  # If it is a long position
            liquidation_price = entry_price * (
                1 - Initial_Margin_Rate + Maintenance_Margin_Rate
            )
            print(f"Leverage : {leverage_value}")
            print(f"Order : {order}")
            # print(f"Account Risk : {self.account_risk_pct}")
            # print(f"Take Profit : {self.take_profit_percent}")
            # print(f"Stop Loss : {self.stop_loss_percent}")

        elif trade_signal == -1:  # If it is a short position
            liquidation_price = entry_price * (
                1 + Initial_Margin_Rate - Maintenance_Margin_Rate
            )
        return liquidation_price

    """
        Execute the trade based on the trading signal and the current price
    """

    def execute_trade(
        self,
        trade_signal,
        current_price,
        i,
    ):
        tp_percent = self.take_profit_percent
        sl_percent = self.stop_loss_percent
        # Check if there is sufficient capital to execute the trade
        if self.capital <= 1:
            print("Insufficient capital to execute trade.")
            return

        if trade_signal != 0 and self.position == 0:
            # Calculate the amount of capital at risk
            trade_risk = self.capital * self.account_risk_pct

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
            liquidation_price = self.EstimatedLiquidationPrice(
                trade_signal, self.entry_price, self.leverage, 0.5
            )
            # Calculate the position size based on leverage, not the total capital
            self.position_size = trade_risk * self.leverage

            # Calculate take profit and stop loss prices
            tp_adjustment = tp_percent if trade_signal == 1 else -tp_percent
            sl_adjustment = -sl_percent if trade_signal == 1 else sl_percent
            tp_price = self.entry_price * (1 + tp_adjustment)
            sl_price = self.entry_price * (1 + sl_adjustment)

            # sl_price = self.entry_price
            self.take_profits.append((i, tp_price))
            self.stop_losses.append((i, sl_price))
            self.liqudation_prices.append((i, liquidation_price))

            print(
                f"Trade {i}: {'Buy' if trade_signal == 1 else 'Sell'} at {self.entry_price}, Trade Risk: {trade_risk} Position Size: {self.position_size} Current Capital: {self.capital}, TP: {tp_price}, SL: {sl_price}, RR: {tp_percent}/ {sl_percent}, Liquidation Price: {liquidation_price}"
            )

    """
        Manage the open trade based on the latest price
    """

    def manage_open_trade(self, latest_price, i):
        if self.position != 0 and self.capital > 0:
            _, tp_price = self.take_profits[-1]
            _, sl_price = self.stop_losses[-1]
            _, liquidation_price = self.liqudation_prices[-1]

            trade_closed = False
            pnl = 0
            # Check if the latest price hits the liquidation price
            if (self.position == 1 and latest_price <= liquidation_price) or (
                self.position == -1 and latest_price >= liquidation_price
            ):
                print(f"Liquidation occurred at {latest_price}")
                # Reset the capital to the amount before the trade and close the position

                self.position = 0
                self.position_size = 0
                self.trade_results.append(0)  # PnL is 0 in case of liquidation
                self.non_profitable_trades.append((i, latest_price))
                return

            # Calculate the PnL based on the risk-to-reward ratio
            if self.position == 1:  # Long position
                if latest_price >= tp_price:
                    pnl = self.position_size * self.take_profit_percent
                    trade_closed = True
                elif latest_price <= sl_price:
                    pnl = -(self.position_size) * self.stop_loss_percent
                    trade_closed = True

            elif self.position == -1:  # Short position
                if latest_price <= tp_price:
                    pnl = self.position_size * self.take_profit_percent
                    trade_closed = True
                elif latest_price >= sl_price:
                    pnl = -(self.position_size) * self.stop_loss_percent
                    trade_closed = True

            if trade_closed:
                # Re-add the risked amount and the PnL to the capital
                self.capital += (self.position_size / self.leverage) + pnl
                self.trade_results.append(pnl)
                self.position = 0  # Reset position
                self.position_size = 0  # Reset position size
                # Record profitable and non-profitable trades
                if pnl > 0:
                    self.profitable_trades.append((i, latest_price))
                else:
                    self.non_profitable_trades.append((i, latest_price))
                print(f"Trade {i} closed with PnL: {pnl}, Capital: {self.capital}")
        else:
            print("Out of capital, cannot trade!")


"""
    Main backtesting method that iterates through the data and checks for trading signals
"""


def backtest(strategy, data, order):
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


if __name__ == "__main__":
    data = pd.read_csv("CurrencyData/preprocessed_data.csv")
    price = data["Close"]

    ERROR_ALLOWED = 10.0 / 100
    order = 4

    strategy = TradingStrategy(
        initial_capital=100,
        leverage=25,
        account_risk_pct=0.45,
        take_profit_percent=0.025,
        stop_loss_percent=0.01,
        slippage_points=2,
    )
    backtest(strategy, data, order)

    # print(f"Total PnL from Trades: {sum(strategy.trade_results)}\n")
    # print(f"Trade Results: {strategy.trade_results}\n")
    # print(f"Entry Points: {strategy.entry_points}\n")
    # print(f"Take Profits: {strategy.take_profits}\n")
    # print(f"Stop Losses: {strategy.stop_losses}\n")
    # print(f"Profitable Trades: {strategy.profitable_trades}\n")
    # print(f"Non-Profitable Trades: {strategy.non_profitable_trades}\n")
    # print(f"Total Trades: {len(strategy.entry_points)}\n")
    print(">>>>> Test Slippage.py <<<<<")
    print(f"Final Capital : ${strategy.capital}\n")
    print(f"Order: {order}")
    print(
        f"Percentage of Profitable Trades: {(100 * len(strategy.profitable_trades))/len(strategy.entry_points)}%"
    )

    """
        Data for plotting 
    """
    entry = strategy.entry_points
    tp = strategy.take_profits
    sl = strategy.stop_losses
    good_trade = strategy.profitable_trades
    bad_trade = strategy.non_profitable_trades
"""
	This is the end of the scipt...
"""
