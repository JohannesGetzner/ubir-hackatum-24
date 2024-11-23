import requests
import random
import time
from typing import Dict, List

def create_and_initialize_scenario() -> dict:
    response = requests.post('http://localhost:3333/create_and_initialize_scenario')
    if response.status_code != 200:
        raise Exception("Failed to create and initialize scenario")
    return response.json()

def launch_scenario(scenario_id: str, speed: float = .2) -> dict:
    response = requests.post(f'http://localhost:3333/launch_scenario/{scenario_id}/{speed}')
    if response.status_code != 200:
        raise Exception("Failed to launch scenario")
    return response.json()

def create_random_assignment(scenario: dict) -> Dict[str, List[str]]:
    vehicles = scenario['scenario']['vehicles']
    customers = scenario['scenario']['customers']
    
    # Create a dictionary of vehicle_id to list of customer_ids
    assignment = {vehicle['id']: [] for vehicle in vehicles}
    
    # Create a list of customer IDs that we can pop from
    customer_ids = [customer['id'] for customer in customers]
    
    # Keep assigning customers until we've assigned all of them
    current_vehicle_idx = 0
    while customer_ids:
        # Get the next customer and vehicle
        customer_id = customer_ids.pop(0)
        vehicle_id = vehicles[current_vehicle_idx]['id']
        
        # Add the customer to the vehicle's list
        assignment[vehicle_id].append(customer_id)
        
        # Move to the next vehicle, wrapping around if necessary
        current_vehicle_idx = (current_vehicle_idx + 1) % len(vehicles)
    
    return assignment

def run_scenario(scenario_id: str, assignment: Dict[str, List[str]]) -> dict:
    response = requests.post(
        f'http://localhost:3333/run_scenario/{scenario_id}',
        json=assignment
    )
    if response.status_code != 200:
        raise Exception("Failed to run scenario")
    return response.json()

def main():
    try:
        # Step 1: Create and initialize scenario
        print("Creating and initializing scenario...")
        scenario_response = create_and_initialize_scenario()
        scenario_id = scenario_response['scenario']['id']
        print(f"Created scenario with ID: {scenario_id}")
        print(f"Number of vehicles: {scenario_response['num_vehicles']}")
        print(f"Number of customers: {scenario_response['num_customers']}")
        
        # Step 2: Launch scenario
        print("\nLaunching scenario...")
        launch_response = launch_scenario(scenario_id)
        print("Scenario launched successfully")
        
        # Step 3: Create random assignment
        print("\nCreating random vehicle-to-customer assignment...")
        assignment = create_random_assignment(scenario_response)
        print(f"Created assignment for {len(assignment)} vehicles")
        
        # Step 4: Run scenario with assignment
        print("\nRunning scenario with assignment...")
        run_response = run_scenario(scenario_id, assignment)
        print("Scenario is now running with the assignments")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
