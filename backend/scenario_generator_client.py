import requests
from typing import List, Optional
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class ResponseMessage:
    message: str

@dataclass
class VehicleDataDto:
    id: UUID
    total_travel_time: int
    total_trips: int
    travel_times: str

@dataclass
class ScenarioMetadataDTO:
    id: UUID
    start_time: str
    end_time: str
    status: str
    vehicle_data: List[VehicleDataDto]

@dataclass
class VehicleDTO:
    id: UUID
    coordX: float
    coordY: float
    isAvailable: bool
    vehicleSpeed: float
    customerId: UUID
    remainingTravelTime: int
    distanceTravelled: float
    activeTime: int
    numberOfTrips: int

@dataclass
class CustomerDTO:
    id: UUID
    coordX: float
    coordY: float
    destinationX: float
    destinationY: float
    awaitingService: bool

@dataclass
class ScenarioDTO:
    id: UUID
    startTime: str
    endTime: str
    status: str
    vehicles: List[VehicleDTO]
    customers: List[CustomerDTO]

class ScenarioGeneratorClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')

    def scenario_json_to_dto(self, scenario_json):
        vehicles = [VehicleDTO(**vehicle) for vehicle in scenario_json.get('vehicles', [])]
        customers = [CustomerDTO(**customer) for customer in scenario_json.get('customers', [])]
        return ScenarioDTO(
            id=UUID(scenario_json['id']) if isinstance(scenario_json['id'], str) else scenario_json['id'],
            startTime=scenario_json['startTime'],
            endTime=scenario_json['endTime'],
            status=scenario_json['status'],
            vehicles=vehicles,
            customers=customers
        )

    def create_scenario(self, num_vehicles: Optional[int] = None, num_customers: Optional[int] = None) -> ScenarioDTO:
        """
        Initialize a random scenario with optional parameters for number of vehicles and customers.
        
        Args:
            num_vehicles: Optional number of vehicles in the scenario
            num_customers: Optional number of customers in the scenario
            
        Returns:
            ScenarioDTO object containing the initialized scenario
        """
        params = {}
        if num_vehicles is not None:
            params['numberOfVehicles'] = num_vehicles
        if num_customers is not None:
            params['numberOfCustomers'] = num_customers
            
        response = requests.post(f"{self.base_url}/scenario/create", params=params)
        response.raise_for_status()
        data = response.json()
        return self.scenario_json_to_dto(data)

    def get_all_scenarios(self) -> List[ScenarioDTO]:
        """
        Get all scenarios.
        
        Returns:
            List of ScenarioDTO objects
        """
        response = requests.get(f"{self.base_url}/scenarios")
        response.raise_for_status()
        return [self.scenario_json_to_dto(scenario) for scenario in response.json()]

    def get_scenario_by_id(self, scenario_id: UUID) -> ScenarioDTO:
        """
        Get a scenario by its ID.
        
        Args:
            scenario_id: UUID of the scenario
            
        Returns:
            ScenarioDTO object
        """
        response = requests.get(f"{self.base_url}/scenarios/{scenario_id}")
        response.raise_for_status()
        return self.scenario_json_to_dto(response.json())

    def delete_scenario_by_id(self, scenario_id: UUID) -> ResponseMessage:
        """
        Delete a scenario by its ID.
        
        Args:
            scenario_id: UUID of the scenario to delete
            
        Returns:
            ResponseMessage containing the result
        """
        response = requests.delete(f"{self.base_url}/scenarios/{scenario_id}")
        response.raise_for_status()
        return ResponseMessage(**response.json())

    def get_scenario_metadata(self, scenario_id: UUID) -> ScenarioMetadataDTO:
        """
        Get metadata for a scenario.
        
        Args:
            scenario_id: UUID of the scenario
            
        Returns:
            ScenarioMetadataDTO object
        """
        response = requests.get(f"{self.base_url}/scenario/{scenario_id}/metadata")
        response.raise_for_status()
        return ScenarioMetadataDTO(**response.json())

    def get_all_vehicles_by_scenario_id(self, scenario_id: UUID) -> List[VehicleDTO]:
        """
        Get all vehicles for a specific scenario.
        
        Args:
            scenario_id: UUID of the scenario
            
        Returns:
            List of StandardMagentaVehicleDTO objects
        """
        response = requests.get(f"{self.base_url}/scenarios/{scenario_id}/vehicles")
        response.raise_for_status()
        return [VehicleDTO(**vehicle) for vehicle in response.json()]

    def get_vehicle_by_id(self, vehicle_id: UUID) -> VehicleDTO:
        """
        Get a vehicle by its ID.
        
        Args:
            vehicle_id: UUID of the vehicle
            
        Returns:
            StandardMagentaVehicleDTO object
        """
        response = requests.get(f"{self.base_url}/vehicles/{vehicle_id}")
        response.raise_for_status()
        return VehicleDTO(**response.json())

    def get_all_customers_by_scenario_id(self, scenario_id: UUID) -> List[CustomerDTO]:
        """
        Get all customers for a specific scenario.
        
        Args:
            scenario_id: UUID of the scenario
            
        Returns:
            List of CustomerDTO objects
        """
        response = requests.get(f"{self.base_url}/scenarios/{scenario_id}/customers")
        response.raise_for_status()
        return [CustomerDTO(**customer) for customer in response.json()]

    def get_customer_by_id(self, customer_id: UUID) -> CustomerDTO:
        """
        Get a customer by their ID.
        
        Args:
            customer_id: UUID of the customer
            
        Returns:
            CustomerDTO object
        """
        response = requests.get(f"{self.base_url}/customers/{customer_id}")
        response.raise_for_status()
        return CustomerDTO(**response.json())
