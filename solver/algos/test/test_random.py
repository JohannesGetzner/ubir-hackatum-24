"""Test the genetic algorithm."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from random_ import solution as random_sol

SCENARIO_NUMBER: int = 3

if __name__ == "__main__":
    with open(
        Path(f"{Path(__file__).parent}/data/scenario_{SCENARIO_NUMBER:>02}.json"), "r"
    ) as f:
        loaded_scenario = json.load(f)
    random_sol.solve(loaded_scenario["vehicles"], loaded_scenario["customers"])
    print("Number of vehicles:", len(loaded_scenario["vehicles"]))
    print("Number of customers:", len(loaded_scenario["customers"]))
