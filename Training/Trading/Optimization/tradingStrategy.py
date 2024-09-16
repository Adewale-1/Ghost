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

    """
        Calculate the estimated liquidation price based on the leverage, entry price and maintenance margin
    """

    def EstimatedLiquidationPrice(
        self, trade_signal, entry_price, position_size, Maintenance_Margin
    ):
        margin = position_size / self.leverage
        Maintenance_Margin_Amount = position_size * (Maintenance_Margin / 100)

        if trade_signal == 1:  # Long position
            liquidation_price = entry_price * (
                1 - (margin - Maintenance_Margin_Amount) / position_size
            )
        elif trade_signal == -1:  # Short position
            liquidation_price = entry_price * (
                1 + (margin - Maintenance_Margin_Amount) / position_size
            )

        return liquidation_price

    """
        Execute the trade based on the trading signal and the current price
    """

    def execute_trade(self, trade_signal, current_price, i):
        tp_percent = self.take_profit_percent
        sl_percent = self.stop_loss_percent

        if self.capital <= 1:
            print("Insufficient capital to execute trade.")
            return

        if trade_signal != 0 and self.position == 0:
            trade_risk = self.capital * self.account_risk_pct

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

            self.position_size = trade_risk * self.leverage
            self.margin = trade_risk  # Store the margin amount

            liquidation_price = self.EstimatedLiquidationPrice(
                trade_signal, self.entry_price, self.position_size, 0.5
            )

            tp_adjustment = tp_percent if trade_signal == 1 else -tp_percent
            sl_adjustment = -sl_percent if trade_signal == 1 else sl_percent
            tp_price = self.entry_price * (1 + tp_adjustment)
            sl_price = self.entry_price * (1 + sl_adjustment)

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
                # The entire margin is lost in case of liquidation
                self.capital -= self.margin
                self.position = 0
                self.position_size = 0
                self.margin = 0
                self.trade_results.append(-self.margin)
                self.non_profitable_trades.append((i, latest_price))
                return

            # Calculate the PnL based on the actual price movement and leverage
            price_change = (latest_price - self.entry_price) / self.entry_price
            if self.position == 1:  # Long position
                pnl = self.position_size * price_change
                if latest_price >= tp_price or latest_price <= sl_price:
                    trade_closed = True
            elif self.position == -1:  # Short position
                pnl = -self.position_size * price_change
                if latest_price <= tp_price or latest_price >= sl_price:
                    trade_closed = True

            if trade_closed:
                # Re-add the margin and the PnL to the capital
                self.capital += self.margin + pnl
                self.trade_results.append(pnl)
                self.position = 0  # Reset position
                self.position_size = 0  # Reset position size
                self.margin = 0  # Reset margin
                # Record profitable and non-profitable trades
                if pnl > 0:
                    self.profitable_trades.append((i, latest_price))
                else:
                    self.non_profitable_trades.append((i, latest_price))
                print(f"Trade {i} closed with PnL: {pnl}, Capital: {self.capital}")
        else:
            print("Out of capital, cannot trade!")
