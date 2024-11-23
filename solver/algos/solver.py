"""High-level solver for taxi commissioning."""

import importlib
import time


def _wrangle_solution(solution: list[tuple[str, str]]):
    """Change the format of the solution.

    The output format is a dictionary indexed by the car id. Each of the values
    is a list of customer ids assigned to a taxi.
    """
    wrangled_solution = {}
    for vehicle, customer in solution:
        wrangled_solution.setdefault(vehicle, []).append(customer)
    return wrangled_solution


def solve(
    vehicles: list[dict],
    customers: list[dict],
) -> dict:
    random_sol = importlib.import_module(".random_.solution", package="algos")
    genetic_sol = importlib.import_module(".genetic.solution", package="algos")
    start_time = time.perf_counter()
    random_sol, random_stats = random_sol.solve(vehicles, customers)
    elapsed_seconds_random = time.perf_counter() - start_time

    start_time = time.perf_counter()
    genetic_sol, genetic_stats = genetic_sol.solve(
        vehicles, customers, max_generations=(len(vehicles) + len(customers)) * 2
    )
    elapsed_seconds_genetic = time.perf_counter() - start_time

    return {
        "random": {
            "allocation": _wrangle_solution(random_sol),
            "stats": {
                "total_distance": random_stats[0],
                "estimated_total_waiting_time": random_stats[1],
            },
            "elapsed_seconds": elapsed_seconds_random,
        },
        "genetic": {
            "allocation": _wrangle_solution(genetic_sol),
            "stats": {
                "total_distance": genetic_stats[0],
                "estimated_total_waiting_time": genetic_stats[1],
            },
            "elapsed_seconds": elapsed_seconds_genetic,
        },
        "saving_rates": {
            "total_distance": 1.0 - (genetic_stats[0] / random_stats[0]),
            "total_waiting_time": 1.0 - (genetic_stats[1] / random_stats[1]),
        },
    }
