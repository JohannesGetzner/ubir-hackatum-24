import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Vehicle:
    id: str
    coordX: float
    coordY: float
    isAvailable: Optional[bool] = None
    vehicleSpeed: Optional[float] = None
    customerId: Optional[str] = None
    remainingTravelTime: Optional[float] = None
    distanceTravelled: Optional[float] = None
    activeTime: Optional[float] = None
    numberOfTrips: Optional[int] = None

@dataclass
class Customer:
    id: str
    coordX: Optional[float] = None
    coordY: Optional[float] = None
    destinationX: Optional[float] = None
    destinationY: Optional[float] = None
    awaitingService: Optional[bool] = None

@dataclass
class Scenario:
    id: str
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    status: Optional[str] = None
    vehicles: Optional[List[Vehicle]] = None
    customers: Optional[List[Customer]] = None

class ScenarioRunnerClient:
    def __init__(self, base_url: str = "http://scenariorunner:8090"):
        self.base_url = base_url.rstrip('/')

    def launch_scenario(self, scenario_id: str, speed: float = 0.2) -> bool:
        """
        Launch a scenario with the specified ID and execution speed.
        
        Args:
            scenario_id: The ID of the scenario to launch
            speed: Execution speed (1.0 for real-time, <1 for faster execution)
        
        Returns:
            bool: True if successful, raises exception otherwise
        """
        url = f"{self.base_url}/Runner/launch_scenario/{scenario_id}"
        response = requests.post(url, params={"speed": speed})
        response.raise_for_status()
        return True

    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """
        Get scenario details by ID.
        
        Args:
            scenario_id: The ID of the scenario to retrieve
            
        Returns:
            Dict containing the scenario data
        """
        url = f"{self.base_url}/Scenarios/get_scenario/{scenario_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def initialize_scenario(self, scenario: Scenario, db_scenario_id: Optional[str] = None) -> bool:
        """
        Initialize a new scenario.
        
        Args:
            scenario: Scenario object containing the scenario data
            db_scenario_id: Optional database scenario ID
            
        Returns:
            bool: True if successful, raises exception otherwise
        """
        url = f"{self.base_url}/Scenarios/initialize_scenario"
        params = {}
        if db_scenario_id:
            params["db_scenario_id"] = db_scenario_id
            
        response = requests.post(
            url,
            json={
                "id": scenario.id,
                "startTime": scenario.startTime,
                "endTime": scenario.endTime,
                "status": scenario.status,
                "vehicles": [vars(v) for v in scenario.vehicles] if scenario.vehicles else None,
                "customers": [vars(c) for c in scenario.customers] if scenario.customers else None
            },
            params=params
        )
        response.raise_for_status()
        return True

    def update_scenario(self, scenario_id: str, vehicle_updates: List[Dict[str, str]]) -> bool:
        """
        Update a scenario with new vehicle assignments.
        
        Args:
            scenario_id: The ID of the scenario to update
            vehicle_updates: List of dicts containing vehicle ID and customer ID assignments
            
        Returns:
            bool: True if successful, raises exception otherwise
        """
        url = f"{self.base_url}/Scenarios/update_scenario/{scenario_id}"
        response = requests.put(
            url,
            json={"vehicles": vehicle_updates}
        )
        response.raise_for_status()
        return True
