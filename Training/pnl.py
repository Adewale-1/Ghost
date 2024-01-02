import numpy as np
from Backtest2 import pnl, order, ERROR_ALLOWED, data

# # Assuming pnl is the array of profits and losses on each trade starting with a $100 account
# # For example, let's create a mock pnl array
# pnl = np.array(pnl)

# initial_account_balance = 1000
# account_balance = initial_account_balance + np.cumsum(pnl)

# # Return on Investment (ROI)
# ROI = (account_balance[-1] - initial_account_balance) / initial_account_balance

# # Calculating the Percentage of Profitable Trades
# number_of_trades = len(pnl)
# number_of_profitable_trades = np.sum(pnl > 0)
# percentage_profitable_trades = (number_of_profitable_trades / number_of_trades) * 100


# # Drawdown
# running_max = np.maximum.accumulate(account_balance)
# drawdown = running_max - account_balance
# max_drawdown = np.max(drawdown)

# # Sharpe Ratio (Assuming pnl represents daily returns, and an annual risk-free rate )
# annual_risk_free_rate = 0.01  # 1% annual risk-free rate for example
# daily_risk_free_rate = (
#     np.power(1 + annual_risk_free_rate, 1 / 252) - 1
# )  # Convert to daily rate
# excess_daily_returns = pnl - daily_risk_free_rate
# sharpe_ratio = (
#     np.sqrt(252) * np.mean(excess_daily_returns) / np.std(excess_daily_returns)
# )

# # MAE and MFE
# MAE = np.min(
#     account_balance - running_max
# )  # Most account balance has been below the running max
# MFE = np.max(
#     account_balance - initial_account_balance
# )  # Most account balance has been above initial

# # Profit Factor
# gross_profit = pnl[pnl > 0].sum()
# gross_loss = -pnl[pnl < 0].sum()
# profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

# print(f"Initial Account Balance: {initial_account_balance} \n")
# print(f"Final Account Balance: {account_balance[-1]} \n")
# print(f"Error Allowed: {ERROR_ALLOWED} \n")
# print(f"Order: {order} \n")
# print(f"Number of Trades: {pnl.size} \n")
# print(f"Return on Investment (ROI): {ROI} \n")
# print(f"Percentage of Profitable Trades: {percentage_profitable_trades:.2f}% \n")
# print(f"Maximum Drawdown: {max_drawdown} \n")
# print(f"Sharpe Ratio: {sharpe_ratio} \n")
# print(f"MAE: {MAE} \n")
# print(f"MFE: {MFE} \n")
# start_date = data["Datetime"]
# print(f"Starting Date: {start_date.iloc[0]} \n")
# print(f"End Date: {start_date.iloc[-1]} \n")

# print(f"Profit Factor: {profit_factor} \n")

pnl = np.array(pnl) / 100  # Convert percentage to a decimal
# pnl = np.array(pnl) / 100

initial_account_balance = 1000  # 100 for the first case, 1000 for the second

account_balances = [initial_account_balance]
for trade_pnl in pnl:
    trade_result = (
        account_balances[-1] * trade_pnl
    )  # Calculate the dollar result of the trade
    new_balance = account_balances[-1] + trade_result
    account_balances.append(new_balance)

account_balance = np.array(account_balances)
ROI = (account_balance[-1] - initial_account_balance) / initial_account_balance

# Profitable Trades Percentage
number_of_trades = len(pnl)
number_of_profitable_trades = np.sum(pnl > 0)
percentage_profitable_trades = (number_of_profitable_trades / number_of_trades) * 100

# Drawdown Calculation
running_max = np.maximum.accumulate(account_balance)
drawdown = running_max - account_balance
max_drawdown = np.max(drawdown)

# Sharpe Ratio Calculation
annual_risk_free_rate = 0.01
daily_risk_free_rate = np.power(1 + annual_risk_free_rate, 1 / 252) - 1
excess_daily_returns = pnl - daily_risk_free_rate
# Ensure pnl is daily returns and not trade P/L for this calculation
sharpe_ratio = (
    np.sqrt(252) * np.mean(excess_daily_returns) / np.std(excess_daily_returns)
    if np.std(excess_daily_returns) != 0
    else np.nan
)

MAE = np.min(pnl)  # Assuming pnl is P/L of individual trades
MFE = np.max(pnl)


# Profit Factor Calculation
gross_profit = np.sum(pnl[pnl > 0])
gross_loss = -np.sum(pnl[pnl < 0])
profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

# Output the results
print(f"Initial Account Balance: {initial_account_balance} \n")
print(f"Final Account Balance: {account_balance[-1]} \n")
print(f"Error Allowed: {ERROR_ALLOWED} \n")
print(f"Order: {order} \n")
print(f"Number of Trades: {pnl.size} \n")
print(f"Return on Investment (ROI): {ROI} \n")
print(f"Percentage of Profitable Trades: {percentage_profitable_trades:.2f}% \n")
print(f"Maximum Drawdown: {max_drawdown} \n")
print(f"Sharpe Ratio: {sharpe_ratio} \n")
print(f"MAE: {MAE} \n")
print(f"MFE: {MFE} \n")
start_date = data["Datetime"]
print(f"Starting Date: {start_date.iloc[0]} \n")
print(f"End Date: {start_date.iloc[-1]} \n")
