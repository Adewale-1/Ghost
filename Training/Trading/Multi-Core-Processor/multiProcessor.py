# import pandas as pd
# import numpy as np
# from scipy.signal import argrelextrema
# import itertools
# import os
# import sys
# import random
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from harmonic_pattern import *
# # from backtestStrategy import TradingStrategy
# import multiprocessing

# rsi_period = 14
# rsi_oversold = 30
# rsi_overbought = 70




# class TradingStrategy:
#     def __init__(self, initial_capital, slippage_points, leverage=1, account_risk_pct=0.01, take_profit_percent=0.02, stop_loss_percent=0.01):
#         self.capital = initial_capital
#         self.position_size = 0
#         self.slippage_points = slippage_points
#         self.position = 0  # 1 for long, -1 for short, 0 for no position
#         self.entry_price = 0
#         self.trade_results = []
#         self.entry_points = []
#         self.take_profits = []
#         self.stop_losses = []
#         self.profitable_trades = []
#         self.non_profitable_trades = []
#         self.leverage = leverage
#         self.account_risk_pct = account_risk_pct
#         self.take_profit_percent = take_profit_percent
#         self.stop_loss_percent = stop_loss_percent

#     def execute_trade(self, trade_signal, current_price, i, atr, reward_risk_ratio=2):
#         if trade_signal != 0 and self.position == 0:  # Only enter if no open position
#             self.position = trade_signal
#             self.position_size = (self.capital * self.account_risk_pct) / atr * self.leverage

#             slippage_range = (1, 5)
#             random_slippage_points = random.randint(*slippage_range) / 10000
#             entry_price_adjustment = random_slippage_points if trade_signal == 1 else -random_slippage_points
#             self.entry_price = current_price + entry_price_adjustment

#             self.entry_points.append((i, self.entry_price))

#             stop_loss_distance = atr * self.stop_loss_percent
#             take_profit_distance = atr * self.take_profit_percent * reward_risk_ratio

#             if trade_signal == 1:
#                 tp_price = self.entry_price + take_profit_distance
#                 sl_price = self.entry_price - stop_loss_distance
#             else:
#                 tp_price = self.entry_price - take_profit_distance
#                 sl_price = self.entry_price + stop_loss_distance

#             self.take_profits.append((i, tp_price))
#             self.stop_losses.append((i, sl_price))

#             print(f"New trade at index {i}: {'Buy' if trade_signal == 1 else 'Sell'} at {self.entry_price}, TP: {tp_price}, SL: {sl_price}")

#     def manage_open_trade(self, latest_close, i):
#         if self.position != 0:
#             existing_trade_index = self.entry_points[-1][0]
#             existing_entry_price = self.entry_points[-1][1]
#             existing_tp_price = self.take_profits[-1][1]
#             existing_sl_price = self.stop_losses[-1][1]

#             exit_slippage = self.slippage_points * 0.0001

#             if self.position == 1:
#                 if latest_close >= existing_tp_price:
#                     exit_price = existing_tp_price - exit_slippage
#                     pnl = (exit_price - existing_entry_price) * self.position_size
#                 elif latest_close <= existing_sl_price:
#                     exit_price = existing_sl_price + exit_slippage
#                     pnl = (exit_price - existing_entry_price) * self.position_size
#                 else:
#                     return

#             elif self.position == -1:
#                 if latest_close <= existing_tp_price:
#                     exit_price = existing_tp_price + exit_slippage
#                     pnl = (existing_entry_price - exit_price) * self.position_size
#                 elif latest_close >= existing_sl_price:
#                     exit_price = existing_sl_price - exit_slippage
#                     pnl = (existing_entry_price - exit_price) * self.position_size
#                 else:
#                     return

#             self.capital += pnl
#             self.trade_results.append(pnl)
#             if pnl > 0:
#                 self.profitable_trades.append((existing_trade_index, exit_price))
#             else:
#                 self.non_profitable_trades.append((existing_trade_index, exit_price))
#             self.position = 0
#             print(f"Trade closed at index {i} with PnL: {pnl}")



# def calculate_atr(prices_df, period=14):
#     high_low = prices_df['High'] - prices_df['Low']
#     high_close = np.abs(prices_df['High'] - prices_df['Close'].shift())
#     low_close = np.abs(prices_df['Low'] - prices_df['Close'].shift())
#     ranges = pd.concat([high_low, high_close, low_close], axis=1)
#     true_range = ranges.max(axis=1)
#     atr = true_range.rolling(period).mean()
#     return atr.iloc[-1]

# def calculate_rsi(prices_df, period=14):
#     delta = prices_df['Close'].diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
#     rs = gain / loss
#     rsi = 100 - (100 / (1 + rs))
#     return rsi

# # Calculate RSI


# def evaluate_combination(combination, data_path, error_allowed):
#     # Load data inside the function to ensure each process has its own copy
#     data = pd.read_csv(data_path)
#     data['RSI'] = calculate_rsi(data, rsi_period)
#     price = data["Close"]

#     leverage, account_risk_pct, take_profit_percent, stop_loss_percent, order = combination
#     strategy = TradingStrategy(
#         initial_capital=100,
#         slippage_points=2,
#         leverage=leverage,
#         account_risk_pct=account_risk_pct,
#         take_profit_percent=take_profit_percent,
#         stop_loss_percent=stop_loss_percent,
#     )

#     for i in range(order, len(data) - 1):
#         current_price = data["Close"].iloc[i]
#         atr = calculate_atr(data.iloc[:i + 1])
#         rsi = data['RSI'].iloc[i]
        
#         if strategy.position == 0:
#             max_idx = argrelextrema(price.values[:i], np.greater, order=order)[0]
#             min_idx = argrelextrema(price.values[:i], np.less, order=order)[0]

#             idx = np.concatenate((max_idx, min_idx, [i - 1]))
#             idx.sort()

#             current_idx = idx[-5:]
#             if len(current_idx) < 5:
#                 continue

#             current_pattern = price.iloc[current_idx].reset_index(drop=True)
#             XA = current_pattern[1] - current_pattern[0]
#             AB = current_pattern[2] - current_pattern[1]
#             BC = current_pattern[3] - current_pattern[2]
#             CD = current_pattern[4] - current_pattern[3]
#             LINES = [XA, AB, BC, CD]

#             pattern_gartley = is_gartley_pattern(LINES, error_allowed)
#             pattern_butterfly = is_butterfly_pattern(LINES, error_allowed)
#             pattern_bat = is_bat_pattern(LINES, error_allowed)
#             pattern_crab = is_crab_pattern(LINES, error_allowed)
#             pattern_cypher = is_cypher_pattern(LINES, error_allowed)
#             pattern_shark = is_shark_pattern(LINES, error_allowed)           
            
#             harmonics = np.array([pattern_gartley, pattern_butterfly, pattern_bat, pattern_crab, pattern_cypher, pattern_shark])

#             if rsi < rsi_oversold:
#                 rsi_signal = 1  # Buy signal
#             elif rsi > rsi_overbought:
#                 rsi_signal = -1  # Sell signal
#             else:
#                 rsi_signal = 0

#             combined_signal = 0
#             if np.any(harmonics == 1) and rsi_signal == 1:
#                 combined_signal = 1
#             elif np.any(harmonics == -1) and rsi_signal == -1:
#                 combined_signal = -1

#             if combined_signal != 0:
#                 strategy.execute_trade(combined_signal, current_price, i, atr)

#         elif strategy.position != 0:
#             latest_close = data["Close"].iloc[i]
#             strategy.manage_open_trade(latest_close, i)

#     final_capital = strategy.capital
#     return final_capital, combination

# if __name__ == "__main__":
#     dataPaths = ["CurrencyData/BTCUSDT_updated.csv", "CurrencyData/ETHUSDT_updated.csv"]
#     error_allowed = 10.0 / 100

#     leverage_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
#     account_risk_pct_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
#     take_profit_percent_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
#     stop_loss_percent_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
#     order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

#     parameter_combinations = list(itertools.product(
#         leverage_values,
#         account_risk_pct_values,
#         take_profit_percent_values,
#         stop_loss_percent_values,
#         order,
#     ))

#     num_processes = multiprocessing.cpu_count()

#     for data_path in dataPaths:
#         with multiprocessing.Pool(processes=num_processes) as pool:
#             results = pool.starmap(
#                 evaluate_combination,
#                 [(combination, data_path, error_allowed) for combination in parameter_combinations],
#             )

#         max_return, best_combination = max(results, key=lambda x: x[0])
#         filename = f"OptimizationMulti-CoreResult_{data_path}.txt"
#         with open(filename, "w") as file:
#             file.write(
#                 f"From File {data_path}\n"
#                 f"Maximum capital return: {max_return}\n"
#                 f"Best parameters for max capital return: Leverage: {best_combination[0]},\n"
#                 f"Account Risk%: {best_combination[1]},\n Take Profit%: {best_combination[2]},\n"
#                 f"Stop Loss%: {best_combination[3]},\n Best order: {best_combination[4]}"
#             )

#         print(
#             f"Best parameters for max capital return: Leverage: {best_combination[0]}, "
#             f"Account Risk%: {best_combination[1]}, Take Profit%: {best_combination[2]}, "
#             f"Stop Loss%: {best_combination[3]}, Best order: {best_combination[4]}"
#         )
#         print(f"Max capital return: {max_return}")



import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import itertools
import os
import sys
import random
import multiprocessing

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harmonic_pattern import *

# RSI parameters
rsi_period = 14
rsi_oversold = 30
rsi_overbought = 70

class TradingStrategy:
    def __init__(self, initial_capital, slippage_points, leverage=1, account_risk_pct=0.01, take_profit_percent=0.02, stop_loss_percent=0.01):
        self.capital = initial_capital
        self.position_size = 0
        self.slippage_points = slippage_points
        self.position = 0  # 1 for long, -1 for short, 0 for no position
        self.entry_price = 0
        self.trade_results = []
        self.entry_points = []
        self.take_profits = []
        self.stop_losses = []
        self.profitable_trades = []
        self.non_profitable_trades = []
        self.leverage = leverage
        self.account_risk_pct = account_risk_pct
        self.take_profit_percent = take_profit_percent
        self.stop_loss_percent = stop_loss_percent

    def execute_trade(self, trade_signal, current_price, i, atr, reward_risk_ratio=2):
        if trade_signal != 0 and self.position == 0:  # Only enter if no open position
            self.position = trade_signal
            self.position_size = (self.capital * self.account_risk_pct) / atr * self.leverage

            slippage_range = (1, 5)
            random_slippage_points = random.randint(*slippage_range) / 10000
            entry_price_adjustment = random_slippage_points if trade_signal == 1 else -random_slippage_points
            self.entry_price = current_price + entry_price_adjustment

            self.entry_points.append((i, self.entry_price))

            stop_loss_distance = atr * self.stop_loss_percent
            take_profit_distance = atr * self.take_profit_percent * reward_risk_ratio

            if trade_signal == 1:
                tp_price = self.entry_price + take_profit_distance
                sl_price = self.entry_price - stop_loss_distance
            else:
                tp_price = self.entry_price - take_profit_distance
                sl_price = self.entry_price + stop_loss_distance

            self.take_profits.append((i, tp_price))
            self.stop_losses.append((i, sl_price))

            print(f"New trade at index {i}: {'Buy' if trade_signal == 1 else 'Sell'} at {self.entry_price}, TP: {tp_price}, SL: {sl_price}")

    def manage_open_trade(self, latest_close, i):
        if self.position != 0:
            existing_trade_index = self.entry_points[-1][0]
            existing_entry_price = self.entry_points[-1][1]
            existing_tp_price = self.take_profits[-1][1]
            existing_sl_price = self.stop_losses[-1][1]

            exit_slippage = self.slippage_points * 0.0001

            if self.position == 1:
                if latest_close >= existing_tp_price:
                    exit_price = existing_tp_price - exit_slippage
                    pnl = (exit_price - existing_entry_price) * self.position_size
                elif latest_close <= existing_sl_price:
                    exit_price = existing_sl_price + exit_slippage
                    pnl = (exit_price - existing_entry_price) * self.position_size
                else:
                    return

            elif self.position == -1:
                if latest_close <= existing_tp_price:
                    exit_price = existing_tp_price + exit_slippage
                    pnl = (existing_entry_price - exit_price) * self.position_size
                elif latest_close >= existing_sl_price:
                    exit_price = existing_sl_price - exit_slippage
                    pnl = (existing_entry_price - exit_price) * self.position_size
                else:
                    return

            self.capital += pnl
            self.trade_results.append(pnl)
            if pnl > 0:
                self.profitable_trades.append((existing_trade_index, exit_price))
            else:
                self.non_profitable_trades.append((existing_trade_index, exit_price))
            self.position = 0
            print(f"Trade closed at index {i} with PnL: {pnl}")

def calculate_atr(prices_df, period=14):
    high_low = prices_df['High'] - prices_df['Low']
    high_close = np.abs(prices_df['High'] - prices_df['Close'].shift())
    low_close = np.abs(prices_df['Low'] - prices_df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(period).mean()
    return atr.iloc[-1]

def calculate_rsi(prices_df, period=14):
    delta = prices_df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def evaluate_combination(combination, data_path, error_allowed):
    # Load data inside the function to ensure each process has its own copy
    data = pd.read_csv(data_path)
    data['RSI'] = calculate_rsi(data, rsi_period)
    price = data["Close"]

    leverage, account_risk_pct, take_profit_percent, stop_loss_percent, order = combination
    strategy = TradingStrategy(
        initial_capital=100,
        slippage_points=2,
        leverage=leverage,
        account_risk_pct=account_risk_pct,
        take_profit_percent=take_profit_percent,
        stop_loss_percent=stop_loss_percent,
    )

    for i in range(order, len(data) - 1):
        current_price = data["Close"].iloc[i]
        atr = calculate_atr(data.iloc[:i + 1])
        rsi = data['RSI'].iloc[i]
        
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
            pattern_cypher = is_cypher_pattern(LINES, error_allowed)
            pattern_shark = is_shark_pattern(LINES, error_allowed)           
            
            harmonics = np.array([pattern_gartley, pattern_butterfly, pattern_bat, pattern_crab, pattern_cypher, pattern_shark])

            if rsi < rsi_oversold:
                rsi_signal = 1  # Buy signal
            elif rsi > rsi_overbought:
                rsi_signal = -1  # Sell signal
            else:
                rsi_signal = 0

            combined_signal = 0
            if np.any(harmonics == 1) and rsi_signal == 1:
                combined_signal = 1
            elif np.any(harmonics == -1) and rsi_signal == -1:
                combined_signal = -1

            if combined_signal != 0:
                strategy.execute_trade(combined_signal, current_price, i, atr)

        elif strategy.position != 0:
            latest_close = data["Close"].iloc[i]
            strategy.manage_open_trade(latest_close, i)

    final_capital = strategy.capital
    return final_capital, combination

if __name__ == "__main__":
    dataPaths = ["/Users/adewaleadenle/Software Development/GitHub Projects/Ghost/Training/Trading/CurrencyData/BTCUSDT_updated.csv", "/Users/adewaleadenle/Software Development/GitHub Projects/Ghost/Training/Trading/CurrencyData/ETHUSDT_updated.csv"]
    error_allowed = 10.0 / 100

    leverage_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    account_risk_pct_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
    take_profit_percent_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    stop_loss_percent_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    parameter_combinations = list(itertools.product(
        leverage_values,
        account_risk_pct_values,
        take_profit_percent_values,
        stop_loss_percent_values,
        order,
    ))

    num_processes = multiprocessing.cpu_count()
    path = 1
    for data_path in dataPaths:
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.starmap(
                evaluate_combination,
                [(combination, data_path, error_allowed) for combination in parameter_combinations],
            )
        path += 1
        max_return, best_combination = max(results, key=lambda x: x[0])
        filename = f"OptimizationMulti-CoreResult_{path}.txt"
        with open(filename, "w") as file:
            file.write(
                f"From File {data_path}\n"
                f"Maximum capital return: {max_return}\n"
                f"Best parameters for max capital return: Leverage: {best_combination[0]},\n"
                f"Account Risk%: {best_combination[1]},\n Take Profit%: {best_combination[2]},\n"
                f"Stop Loss%: {best_combination[3]},\n Best order: {best_combination[4]}"
            )

        print(
            f"Best parameters for max capital return: Leverage: {best_combination[0]}, "
            f"Account Risk%: {best_combination[1]}, Take Profit%: {best_combination[2]}, "
            f"Stop Loss%: {best_combination[3]}, Best order: {best_combination[4]}"
        )
        print(f"Max capital return: {max_return}")
