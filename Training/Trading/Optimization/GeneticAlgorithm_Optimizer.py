import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from harmonic_pattern import *
from Trading.mainBackTest import TradingStrategy  # This should be your TradingStrategy class
from deap import base, creator, tools, algorithms
import random
import os
import contextlib

# Load pre-processed data (ensure the CSV path is correct)
data = pd.read_csv("CurrencyData/preprocessed_data3.csv")
price = data["Close"]
ERROR_ALLOWED = 10.0 / 100


def evaluate_strategy(
    leverage, account_risk_pct, take_profit_percent, stop_loss_percent, order
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

    final_capital = strategy.capital
    return final_capital


# Genetic Algorithm Functions


# Fitness evaluation function
def fitness(individual):
    (
        leverage,
        account_risk_pct,
        take_profit_percent,
        stop_loss_percent,
        order,
    ) = individual
    return (
        evaluate_strategy(
            leverage,
            account_risk_pct,
            take_profit_percent,
            stop_loss_percent,
            order,
        ),
    )


# Define bounds for the GA parameters (make sure to use integers for discrete parameters)
GA_BOUNDS = [
    (10, 100),  # Leverage
    (5, 50),  # Account risk percentage
    (1, 10),  # Take profit percentage
    (1, 10),  # Stop loss percentage
    (1, 10),  # Order
]


def random_value_from_bounds(bounds):
    return random.randint(*bounds)


# Initialize DEAP

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", random_value_from_bounds, GA_BOUNDS[0])
toolbox.register("attr_risk_pct", random_value_from_bounds, GA_BOUNDS[1])
toolbox.register("attr_take_profit", random_value_from_bounds, GA_BOUNDS[2])
toolbox.register("attr_stop_loss", random_value_from_bounds, GA_BOUNDS[3])
toolbox.register("attr_order", random_value_from_bounds, GA_BOUNDS[4])
toolbox.register(
    "individual",
    tools.initCycle,
    creator.Individual,
    (
        toolbox.attr_float,
        toolbox.attr_risk_pct,
        toolbox.attr_take_profit,
        toolbox.attr_stop_loss,
        toolbox.attr_order,
    ),
    n=1,
)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register(
    "mutate",
    tools.mutUniformInt,
    low=[bound[0] for bound in GA_BOUNDS],
    up=[bound[1] for bound in GA_BOUNDS],
    indpb=0.2,
)
toolbox.register("select", tools.selTournament, tournsize=3)


def main():
    # Create initial population (e.g. 300 individuals)
    population = toolbox.population(n=300)

    # Number of generations
    NGEN = 40
    # Probability of mating two individuals
    CXPB = 0.7
    # Probability of mutating an individual
    MUTPB = 0.2

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    # Extracting all the fitnesses of individuals
    fits = [ind.fitness.values[0] for ind in population]

    # Evolutionary loop
    for g in range(NGEN):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalids = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalids)
        for ind, fit in zip(invalids, fitnesses):
            ind.fitness.values = fit

        # Replace the old population by the offspring
        population[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in population]

        length = len(population)
        mean = sum(fits) / length
        sum_sq = sum(x * x for x in fits)
        std = abs(sum_sq / length - mean**2) ** 0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)

    best_individual = tools.selBest(population, 1)[0]
    print(
        "Best individual is %s, %s" % (best_individual, best_individual.fitness.values)
    )
    return population, best_individual


if __name__ == "__main__":
    population, best_individual = main()

    # Save the best individual (best trading strategy parameters)
    with open("OptimizationResult_Genetic.txt", "w") as file:
        file.write(
            f"Best trading strategy parameters:\n"
            f"Leverage: {int(best_individual[0])}\n"
            f"Account Risk: {best_individual[1]}\n"
            f"Take Profit: {best_individual[2]}\n"
            f"Stop Loss: {best_individual[3]}\n"
            f"Order: {int(best_individual[4])}\n"
            f"Max capital return achieved: {best_individual.fitness.values[0]}\n"
        )
