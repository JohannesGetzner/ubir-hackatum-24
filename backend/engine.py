import logging
import time
from typing import Optional, Dict, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone
import math

from scenario_generator_client import ScenarioGeneratorClient
from scenario_runner_client import ScenarioRunnerClient, Scenario as RunnerScenario
from database.repositories import ScenarioRepository, VehicleRepository, CustomerRepository, AssignmentRepository
from models.scenario import Scenario
from models.vehicle import Vehicle, VehicleRouteStatus
from models.customer import Customer
from models.assignment import Assignment, AssignmentStatus
from models.base import ScenarioStatus
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScenarioEngine:
    def __init__(
        self,
        db: Session,
        generator_url: str = "http://localhost:8080",
        runner_url: str = "http://localhost:8090"
    ):
        self.generator = ScenarioGeneratorClient(generator_url)
        self.runner = ScenarioRunnerClient(runner_url)
        self.scenario_repo = ScenarioRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.assignment_repo = AssignmentRepository(db)


    def create_scenario(
        self,
        num_vehicles: Optional[int] = None,
        num_customers: Optional[int] = None
    ) -> Optional[UUID]:
        # Step 1: Generate scenario
        logger.info("Generating new scenario...")
        scenario_dto = self.generator.create_scenario(
            num_vehicles=num_vehicles,
            num_customers=num_customers
        )
        
        # Create database scenario
        db_scenario = Scenario(
            scenario_id=str(scenario_dto.id),  # Convert UUID to string
            start_time=datetime.now(),
            status=ScenarioStatus.CREATED,
            num_vehicles=num_vehicles,
            num_customers=num_customers
        )
        self.scenario_repo.create(db_scenario)

        logger.info("Saving vehicles to database...")
        for vehicle_dto in scenario_dto.vehicles:
            vehicle = Vehicle(
                scenario_id=str(scenario_dto.id),
                vehicle_id=str(vehicle_dto.id),
                coord_x=vehicle_dto.coordX,
                coord_y=vehicle_dto.coordY
            
            )
            self.vehicle_repo.create(vehicle)

        logger.info("Saving customers to database...")
        for customer_dto in scenario_dto.customers:
            customer = Customer(
                scenario_id=str(scenario_dto.id),
                customer_id=str(customer_dto.id),
                coord_x=customer_dto.coordX,
                coord_y=customer_dto.coordY,
                destination_x=customer_dto.destinationX,
                destination_y=customer_dto.destinationY,
                awaiting_service=True 
            )
            self.customer_repo.create(customer)
        
        # Convert DTO to Runner's Scenario format
        runner_scenario = RunnerScenario(
            id=str(scenario_dto.id),
            startTime=scenario_dto.startTime,
            endTime=None,
            status="RUNNING",
            customers=scenario_dto.customers,
            vehicles=scenario_dto.vehicles
        )
        return scenario_dto


    def initialize_scenario(self, scenario: Scenario) -> bool:
        # Step 2: Initialize scenario in runner
        logger.info(f"Initializing scenario {scenario.id}...")
        success = self.runner.initialize_scenario(scenario)
        logger.info(f"Successfully created and initialized scenario {scenario.id}")
        return True


    def launch_scenario(self, scenario_id:str, speed:float):
        # Step 3: Launch scenario
        logger.info(f"Launching scenario {scenario_id}")
        response = self.runner.launch_scenario(scenario_id=scenario_id,speed=speed)
        start_time = datetime.strptime(response["startTime"], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
        self.scenario_repo.update(Scenario(scenario_id=scenario_id, status=ScenarioStatus.RUNNING, start_time=start_time))
        logger.info(f"Successfully launched scenario")
        return True
            
       
    def create_assignment_in_db(self, scenario_id: str, vehicle_id: str, customer_id: str) -> Assignment:
        now = datetime.now(timezone.utc)
        assignment = Assignment(
            assignment_id=str(uuid4()),
            scenario_id=scenario_id,
            vehicle_id=vehicle_id,
            customer_id=customer_id,
            assignment_start_time=now,
            assignment_end_time=None, 
            distance_travelled=0.0,
            status=AssignmentStatus.IN_PROGRESS
        )
        created_assignment = self.assignment_repo.create(assignment)
        logger.info(f"Created new assignment {created_assignment.assignment_id} for vehicle {vehicle_id} and customer {customer_id}")
        return created_assignment


    def handle_completed_assignments(self, scenario_id: str, available_vehicles: list):
        now = datetime.now(timezone.utc)
        for vehicle in available_vehicles:
            active_assignments = self.assignment_repo.get_by_vehicle(scenario_id, vehicle["id"])
            for assignment in active_assignments:
                if assignment.status == AssignmentStatus.IN_PROGRESS:
                    assignment.status = AssignmentStatus.COMPLETED
                    assignment.assignment_end_time = now
                    assignment.distance_travelled = vehicle.get("distanceTravelled", 0.0)
                    self.assignment_repo.update(assignment)
                    logger.info(f"Completed assignment {assignment.assignment_id} for vehicle {vehicle['id']} with distance {assignment.distance_travelled}")


    def update_assignment_after_step(self, scenario_id:str, assignment: Dict, updated_vehicles: list):
        for vehicle_update in updated_vehicles:
            vehicle_id = vehicle_update["id"]
            if vehicle_id in assignment and len(assignment[vehicle_id]) > 0:
                self.create_assignment_in_db(
                    scenario_id=str(scenario_id),
                    vehicle_id=vehicle_id,
                    customer_id=vehicle_update["customerId"]
                )
                assignment[vehicle_id].pop(0)
        return assignment


    def update_vehicles_in_db(self, scenario_id, vehicles):
        for v in vehicles:
            db_vehicle = Vehicle.from_dict(scenario_id, v)
            v_curr_coord_x, v_curr_coord_y, = self.calculate_vehicle_and_customer_position(db_vehicle, db_vehicle.current_customer_id)
            db_vehicle.current_coord_x = v_curr_coord_x
            db_vehicle.current_coord_y = v_curr_coord_y
            self.vehicle_repo.update(db_vehicle)


    def calculate_haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on Earth in meters
        using the Haversine formula.
        """
        R = 6371000  # Earth's radius in meters
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def calculate_intermediate_position(self, lat1: float, lon1: float, lat2: float, lon2: float, progress: float) -> Tuple[float, float]:
        """
        Calculate an intermediate position between two points on Earth using spherical interpolation.
        progress should be between 0 and 1, where 0 is the start point and 1 is the end point.
        Returns (latitude, longitude) in degrees.
        """
        if progress <= 0:
            return lat1, lon1
        if progress >= 1:
            return lat2, lon2

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        d = math.acos(
            math.sin(lat1) * math.sin(lat2) +
            math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        )
        
        if abs(d) < 1e-10:  # Points are very close
            return math.degrees(lat1), math.degrees(lon1)
            
        a = math.sin((1-progress) * d) / math.sin(d)
        b = math.sin(progress * d) / math.sin(d)
        
        x = a * math.cos(lat1) * math.cos(lon1) + b * math.cos(lat2) * math.cos(lon2)
        y = a * math.cos(lat1) * math.sin(lon1) + b * math.cos(lat2) * math.sin(lon2)
        z = a * math.sin(lat1) + b * math.sin(lat2)
        
        lat = math.atan2(z, math.sqrt(x*x + y*y))
        lon = math.atan2(y, x)
        
        return math.degrees(lat), math.degrees(lon)

    def calculate_vehicle_and_customer_position(self, vehicle: Vehicle, customer_id: str = None) -> tuple[float, float]:
        if not customer_id or vehicle.remaining_travel_time <= 0:
            vehicle.enroute = VehicleRouteStatus.IDLE
            self.vehicle_repo.update(vehicle)
            return vehicle.coord_x, vehicle.coord_y
        else:
            customer = self.customer_repo.get(vehicle.scenario_id, customer_id)
        
        # Get the active assignment for this vehicle
        active_assignment = self.assignment_repo.get_active_assignment(vehicle.scenario_id, vehicle.vehicle_id)
        if not active_assignment:
            vehicle.enroute = VehicleRouteStatus.IDLE
            self.vehicle_repo.update(vehicle)
            return vehicle.coord_x, vehicle.coord_y
        
        # If customer is not picked up yet, calculate distance to customer
        # If customer is picked up, calculate distance to destination
        if not customer.picked_up:
            target_x, target_y = customer.coord_x, customer.coord_y
            vehicle.enroute = VehicleRouteStatus.TO_CUSTOMER
        else:
            target_x, target_y = customer.destination_x, customer.destination_y
            vehicle.enroute = VehicleRouteStatus.TO_DESTINATION
        self.vehicle_repo.update(vehicle)
        
        # Calculate the total distance between current position and target
        total_distance = self.calculate_haversine_distance(
            vehicle.coord_x, vehicle.coord_y,
            target_x, target_y
        )
        
        if total_distance == 0:
            # If we've reached the customer's original position and they're not picked up yet
            if not customer.picked_up and target_x == customer.coord_x and target_y == customer.coord_y:
                customer.picked_up = True
                self.customer_repo.update(customer)
                vehicle.enroute = VehicleRouteStatus.TO_DESTINATION
                self.vehicle_repo.update(vehicle)
                # Return current position, next iteration will start moving to destination
                return vehicle.coord_x, vehicle.coord_y
            return vehicle.coord_x, vehicle.coord_y
        
        # Calculate distance covered based on speed (m/s) and remaining time (seconds)
        distance_covered = total_distance - (vehicle.vehicle_speed * vehicle.remaining_travel_time)
        
        # Calculate progress as ratio of distance covered to total distance
        progress = min(distance_covered / total_distance, 1.0)
        logging.info(f"Progress: {progress}")
        logging.info(f"Remaining travel time: {vehicle.remaining_travel_time}")
        logging.info(f"Distance covered: {distance_covered:.2f}m of {total_distance:.2f}m")
        
        # Calculate the current position by interpolating between start and end points
        current_x, current_y = self.calculate_intermediate_position(
            vehicle.coord_x, vehicle.coord_y,
            target_x, target_y,
            progress
        )
        
        # If we're very close to the customer and they're not picked up yet, pick them up
        if not customer.picked_up and progress > 0.95:
            customer.picked_up = True
            self.customer_repo.update(customer)
            vehicle.enroute = VehicleRouteStatus.TO_DESTINATION
            self.vehicle_repo.update(vehicle)
        
        # If the customer is picked up, update their position to match the vehicle
        if customer.picked_up:
            customer.coord_x = current_x
            customer.coord_y = current_y
            self.customer_repo.update(customer)
        
        logging.info(f"Current position: ({current_x:.6f}, {current_y:.6f}), Target position: ({target_x:.6f}, {target_y:.6f})")
        return current_x, current_y


    def run_scenario(self, scenario_id:str, assignment:Dict):
        current_assignment = {k: v.copy() for k, v in assignment.items()}
        total_customers = sum(len(customers) for customers in current_assignment.values())
        total_vehicles = len(current_assignment)
        logger.info(f"Starting scenario with {total_customers} customers and {total_vehicles} vehicles")
        
        initial_batch = [
            {
                "id": vehicle,
                "customerId": customer_ids[0],
            }
            for vehicle, customer_ids in current_assignment.items()
            if len(customer_ids) > 0
        ]
        response = self.runner.update_scenario(
            scenario_id,
            initial_batch
        )
        time.sleep(1)
        logging.info("Made initial assignment.")
        current_assignment = self.update_assignment_after_step(scenario_id, current_assignment, initial_batch)
        while True:
            remaining_customers = sum(len(v) for v in current_assignment.values())
            if all(len(v) == 0 for v in current_assignment.values()):
                logger.info("All customers have been assigned. Scenario complete.")
                break
                
            scenario = self.runner.get_scenario(scenario_id)
            self.update_vehicles_in_db(scenario_id, scenario["vehicles"]) 
            available_vehicles = [v for v in scenario["vehicles"] if v["isAvailable"] and v["id"] in assignment.keys()]
            busy_vehicles = len(assignment) - len(available_vehicles)
            
            logger.info(f"Status: {remaining_customers} customers remaining | {len(available_vehicles)} vehicles free | {busy_vehicles} vehicles occupied")
            
            self.handle_completed_assignments(scenario_id, available_vehicles)
            updates = []
            for v in available_vehicles:
                if v["id"] in current_assignment and len(current_assignment[v["id"]]) > 0:
                    updates.append({
                        "id": v["id"],
                        "customerId": current_assignment[v["id"]][0],
                    })
                    logging.info(f"Assigning vehicle {v['id']} to customer {current_assignment[v['id']][0]}")
            if updates:
                response = self.runner.update_scenario(scenario_id, updates)
                time.sleep(1)
                current_assignment = self.update_assignment_after_step(scenario_id, current_assignment, updates)
            time.sleep(1)
        return True