import pandas as pd
import numpy as np
from bayesian_optimization import (
    walk_forward_analysis,
    evaluate_strategy,
    strategy_wrapper,
)

# Load pre-processed data
data = pd.read_csv(
    "/Users/adewaleadenle/Software Development/GitHub Projects/Ghost/Training/Trading/CurrencyData/preprocessed_data2.csv"
)

# Define bounds for Bayesian Optimization
bounds = {
    "leverage": (5, 20),
    "account_risk_pct": (5, 25),
    "take_profit_percent": (1, 10),
    "stop_loss_percent": (1, 10),
    "order": (1, 10),
    "error_allowed": (0.1, 0.8),
}

# Define window size and step size for Walk-Forward Analysis
window_size = 252 * 2  # 2 years of daily data
step_size = 252  # 1 year step

# Perform Walk-Forward Analysis
wfa_results, all_best_params = walk_forward_analysis(
    data=data,
    window_size=window_size,
    step_size=step_size,
    optimization_func=strategy_wrapper,
    evaluation_func=evaluate_strategy,
)

# Analyze results
average_return = np.mean(wfa_results)
std_return = np.std(wfa_results)

print(f"Walk-Forward Analysis Results:")
print(f"Average Return: {average_return:.2f}")
print(f"Standard Deviation of Returns: {std_return:.2f}")
print(f"Sharpe Ratio (assuming risk-free rate of 0): {average_return / std_return:.2f}")

# Analyze best parameters
param_names = list(all_best_params[0].keys())
avg_params = {
    param: np.mean([period_params[param] for period_params in all_best_params])
    for param in param_names
}
std_params = {
    param: np.std([period_params[param] for period_params in all_best_params])
    for param in param_names
}

print("\nAverage Best Parameters:")
for param, value in avg_params.items():
    print(f"{param}: {value:.4f} (±{std_params[param]:.4f})")

# Find the parameters of the best performing period
best_period_index = np.argmax(wfa_results)
best_period_params = all_best_params[best_period_index]

print("\nParameters of Best Performing Period:")
for param, value in best_period_params.items():
    print(f"{param}: {value}")

# Saving results
with open("WalkForwardAnalysis_ResultsV5.txt", "w") as file:
    file.write(f"Walk-Forward Analysis Results:\n")
    file.write(f"Average Return: {average_return:.2f}\n")
    file.write(f"Standard Deviation of Returns: {std_return:.2f}\n")
    file.write(
        f"Sharpe Ratio (assuming risk-free rate of 0): {average_return / std_return:.2f}\n"
    )
    file.write(f"\nIndividual Period Returns:\n")
    for i, result in enumerate(wfa_results):
        file.write(f"Period {i+1}: {result:.2f}\n")
    file.write("\nAverage Best Parameters:\n")
    for param, value in avg_params.items():
        file.write(f"{param}: {value:.4f} (±{std_params[param]:.4f})\n")

    file.write("\nParameters of Best Performing Period:\n")
    for param, value in best_period_params.items():
        file.write(f"{param}: {value}\n")
