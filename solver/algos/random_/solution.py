"""Random taxi commissioning."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models import Scenario


def solve(
    vehicles: list[dict],
    customers: list[dict],
) -> list[tuple[int, int]]:
    """Solve a taxi commission with random allocations."""
    scenario = Scenario(vehicles, customers)
    solution = []
    vehicles_idx = list(scenario.indexed_vehicles)
    customers_idx = list(scenario.indexed_customers)
    random.shuffle(customers_idx)
    for customer in customers_idx:
        solution.append((random.choice(vehicles_idx), customer))
    return scenario.solution_to_real_ids(solution), scenario.calculate_cost(solution)
