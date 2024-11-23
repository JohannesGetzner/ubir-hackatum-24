import random
import sys
from functools import partial
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from deap import base, creator, tools

from .utils import eaSimpleWithElitism

sys.path.insert(0, str(Path(__file__).parent.parent))
from models import Scenario

# Define the problem constraints.
POPULATION_SIZE = 500
P_CROSSOVER = 0.9
P_MUTATION = 0.1
MAX_GENERATIONS = 300
HALL_OF_FAME_SIZE = 30

# Define random seed.
RANDOM_SEED = 13
random.seed(RANDOM_SEED)


def _commission_taxi(
    assigned_customers: set[int], num_taxis: int, num_customers: int
) -> tuple[int, int] | None:
    """Assign a taxi to a waiting customer."""
    available_customers = [
        c for c in range(1, num_customers + 1) if c not in assigned_customers
    ]
    if available_customers:
        customer = random.choice(available_customers)
        taxi = random.randint(1, num_taxis)
        assigned_customers.add(customer)
        return (taxi, customer)
    return None


def _create_individual(num_taxis, num_customers):
    """Define a function to create the individual."""
    assigned_customers = set()
    individual = []
    while len(individual) < num_customers:
        commission = _commission_taxi(assigned_customers, num_taxis, num_customers)
        if commission:
            individual.append(commission)
    return individual


def _cxModifiedTwoPoint(ind1, ind2):
    """Modification of the two-point crossover to respect our problem's constraints.

    That is, after the crossover, no individual should have repeated customers.
    The individuals are modified in-place.
    """
    vehicles1 = [gen[0] for gen in ind1]
    vehicles2 = [gen[0] for gen in ind2]
    tools.crossover.cxTwoPoint(vehicles1, vehicles2)
    ind1[0 : len(ind1)] = [(vehicle, gen[1]) for vehicle, gen in zip(vehicles1, ind1)]
    ind2[0 : len(ind2)] = [(vehicle, gen[1]) for vehicle, gen in zip(vehicles2, ind2)]

    return ind1, ind2


def solve(
    vehicles: list[dict],
    customers: list[dict],
    weight_distance: float = 1.0,
    weight_active_time: float= 0.1,
    weight_waiting_time: float = 0.5,
    population_size=POPULATION_SIZE,
    p_crossover=P_CROSSOVER,
    p_mutation=P_MUTATION,
    max_generations=MAX_GENERATIONS,
    hall_of_fame_size=HALL_OF_FAME_SIZE,
) -> list[tuple[int, int]]:
    """Solve a taxi commission problem with a genetic algorithm."""
    scenario = Scenario(vehicles, customers)

    # Optimization objectives.
    creator.create(
        "FitnessMulti",
        base.Fitness,
        weights=(-weight_distance, weight_active_time, -weight_waiting_time),
    )
    # Define the individual type.
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    # Create the toolbox.
    toolbox = base.Toolbox()
    toolbox.register(
        "individual",
        tools.initIterate,
        creator.Individual,
        partial(
            _create_individual, num_taxis=len(vehicles), num_customers=len(customers)
        ),
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Register the evaluation function.
    toolbox.register("evaluate", scenario.calculate_cost)

    # Register the genetic operators.
    toolbox.register("mate", _cxModifiedTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=1.0 / len(customers))
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Create the statistics object.
    stats = tools.Statistics(lambda ind: ind.fitness.values)

    # Register the statistics object.
    stats.register("avg", np.mean, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    # Run the evolutionary algorithm
    hof = tools.HallOfFame(hall_of_fame_size)
    population, logbook = eaSimpleWithElitism(
        toolbox.population(n=population_size),
        toolbox,
        cxpb=p_crossover,
        mutpb=p_mutation,
        ngen=max_generations,
        stats=stats,
        halloffame=hof,
        verbose=True,
    )

    # Print the best ever individual.
    print("Best Individual")
    print("===============")
    print(hof.items[0])
    print("With fitness values of:", hof.items[0].fitness)

    # Return the min and mean values.
    mean_fitness_vals, min_fitness_vals, max_fitness_vals = logbook.select("avg", "min", "max")

    mean_fitness_vals = np.array(mean_fitness_vals)
    min_fitness_vals = np.array(min_fitness_vals)
    max_fitness_vals = np.array(max_fitness_vals)

    mean_distance_vals = mean_fitness_vals[:, 0]
    min_distance_vals = min_fitness_vals[:, 0]
    max_distance_vals = max_fitness_vals[:, 0]

    mean_active_vals = mean_fitness_vals[:, 1]
    min_active_vals = min_fitness_vals[:, 1]
    max_active_vals = max_fitness_vals[:, 1]

    mean_waiting_vals = mean_fitness_vals[:, 2]
    min_waiting_vals = min_fitness_vals[:, 2]
    max_waiting_vals = max_fitness_vals[:, 2]

    # Plot the max and mean values.
    plt.plot(mean_distance_vals, color="blue", label="Mean Distance")
    plt.plot(min_distance_vals, color="green", label="Min. Distance")
    plt.plot(max_distance_vals, color="red", label="Max. Distance")

    plt.plot(mean_active_vals, color="blue", label="Mean Active Time")
    plt.plot(min_active_vals, color="green", label="Min. Active Time")
    plt.plot(max_active_vals, color="red", label="Max. Active Time")

    plt.plot(mean_waiting_vals, color="blue", label="Mean Waiting Time")
    plt.plot(min_waiting_vals, color="green", label="Min. Waiting Time")
    plt.plot(max_waiting_vals, color="red", label="Max. Waiting Time")

    plt.legend(loc="lower right")
    plt.xlabel("Generation")
    plt.ylabel("Optimization Targets")
    plt.title("Optimization Targets over Generations")
    plt.show()
