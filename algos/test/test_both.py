"""Test the genetic algorithm."""

import json
import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).parent.parent))
from solver import solve

SCENARIO_NUMBER: int = 2

if __name__ == "__main__":
    with open(
        Path(f"{Path(__file__).parent}/data/scenario_{SCENARIO_NUMBER:>02}.json"), "r"
    ) as f:
        loaded_scenario = json.load(f)
    solution = solve(loaded_scenario["vehicles"], loaded_scenario["customers"])
    pprint(solution, indent=4)
