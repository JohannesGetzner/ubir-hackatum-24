import logging
from re import X
import secrets
import time
from typing import Optional, Dict, Tuple, List
from uuid import UUID, uuid4
from datetime import datetime, timezone
import math
import requests
from scenario_generator_client import ScenarioGeneratorClient, ScenarioDTO, VehicleDTO
from scenario_runner_client import ScenarioRunnerClient
from database.repositories import ScenarioRepository, VehicleRepository, CustomerRepository, AssignmentRepository
from models.scenario import Scenario
from models.vehicle import Vehicle, VehicleRouteStatus
from models.customer import Customer
from models.assignment import Assignment, AssignmentStatus
from models.base import ScenarioStatus
from sqlalchemy.orm import Session
from dataclasses import asdict

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
        self.active_scenario = None
        self.active_assignment = None
        self.previous_remaining_time_per_vehicle = {}

    def create_and_initialize_scenario(
        self,
        num_vehicles: Optional[int] = None,
        num_customers: Optional[int] = None,
        speed: Optional[float] = None
    ) -> str:
        # Step 1: Generate scenario
        logger.info("Generating new scenario...")
        scenario_dto = self.generator.create_scenario(
            num_vehicles=num_vehicles,
            num_customers=num_customers
        )
        
        # Step 2: Call solver
        scenario_solution = self.call_solver(scenario_dto)


        logger.info("Saving scenario to database...")
        self.scenario_repo.create(Scenario(
            scenario_id=str(scenario_dto.id),  # Convert UUID to string
            start_time=datetime.now(),
            status=ScenarioStatus.CREATED,
            num_vehicles=num_vehicles,
            num_customers=num_customers,
            savings_km_genetic=scenario_solution["saving_rates"]["total_distance"],
            savings_time_genetic=scenario_solution["saving_rates"]["total_waiting_time"]
        ))

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
        logger.info(f"Successfully created scenario {scenario_dto.id}") 
        logger.info(f"Initializing scenario {scenario_dto.id}...")
        success = self.runner.initialize_scenario(scenario_dto)
        logger.info(f"Successfully initialized scenario {scenario_dto.id}")
        self.active_scenario = str(scenario_dto.id)
        self.active_assignment = scenario_solution["genetic"]["allocation"]
        return scenario_dto.id


    def launch_scenario(self, scenario_id:str, speed:float):
        # Step 3: Launch scenario
        logger.info(f"Launching scenario {scenario_id}")
        response = self.runner.launch_scenario(scenario_id=scenario_id,speed=speed)
        start_time = datetime.strptime(response["startTime"], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
        self.scenario_repo.update(Scenario(scenario_id=scenario_id, status=ScenarioStatus.RUNNING, start_time=start_time))
        logger.info(f"Successfully launched scenario")
        return True


    def make_initial_assignment(self):
        initial_batch = [
            {
                "id": vehicle_id,
                "customerId": customer_ids[0],
            }
            for vehicle_id, customer_ids in self.active_assignment.items()
            if len(customer_ids) > 0
        ]
        response = self.runner.update_scenario(
            self.active_scenario,
            initial_batch
        )
        logging.info(f"Made initial assignment. {len(initial_batch)} vehicles assigned.")
        return [assignment["id"] for assignment in initial_batch], [assignment["customerId"] for assignment in initial_batch]


    def update_assignment_after_step(self, active_vehicles: List[str], active_customers: List[str]):
        for v, c in zip(active_vehicles,active_customers):
            if v in self.active_assignment and len(self.active_assignment[v]) > 0:
                self.create_assignment(
                    vehicle_id=v,
                    customer_id=c
                )
                self.active_assignment[v].pop(0)
    

    def create_assignment(self, vehicle_id: str, customer_id: str) -> None:
        now = datetime.now(timezone.utc)
        assignment = Assignment(
            assignment_id=str(uuid4()),
            scenario_id=self.active_scenario,
            vehicle_id=vehicle_id,
            customer_id=customer_id,
            assignment_start_time=now,
            assignment_end_time=None, 
            distance_travelled=0.0,
            status=AssignmentStatus.IN_PROGRESS
        )
        created_assignment = self.assignment_repo.create(assignment)
        logger.info(f"Created new assignment {created_assignment.assignment_id} for vehicle {vehicle_id} and customer {customer_id}")

    
    def calculate_vehicle_position(self, vehicle:Vehicle, target_lat:float=None, target_long:float=None) -> Tuple[float, float]:
        def calculate_intermediate_position(lat1: float, lon1: float, lat2: float, lon2: float, progress: float) -> Tuple[float, float]:
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

        def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            R = 6371000 
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        # Get the original total distance for this leg of the journey
        total_distance = calculate_haversine_distance(vehicle.coord_x, vehicle.coord_y, target_lat, target_long)
        if total_distance == 0:
            total_distance = 1
        start_lat = vehicle.coord_x
        start_long = vehicle.coord_y

        # check if we missed the turning point -> didn't update fast enough and remaining travel time incremented, not decreasing
        if vehicle.remaining_travel_time > self.previous_remaining_time_per_vehicle.get(vehicle.vehicle_id, 9999999):
            logger.info(f"Vehicle {vehicle.vehicle_id} missed the turning point. Catching up by setting progress == 1")
            progress = 1
            distance_covered = total_distance
        else:
            # Calculate distance covered based on original total distance
            distance_covered = total_distance - (vehicle.vehicle_speed * vehicle.remaining_travel_time if vehicle.remaining_travel_time is not None else 0)
            # Calculate progress based on original total distance
            progress = max(0, min(1, distance_covered / total_distance))

        # Calculate intermediate position from current position to target
        intermediate_lat, intermediate_long = calculate_intermediate_position(
            start_lat, start_long,
            target_lat, target_long,
            progress
        )
        # log where the care is and where its going and how far it is
        logger.info(f"Vehicle {vehicle.vehicle_id} is {round(progress * 100, 2)}% of the way to {target_lat, target_long}; state: {vehicle.enroute}; origin: {vehicle.coord_x, vehicle.coord_y}; current: {intermediate_lat, intermediate_long}; total distance: {round(total_distance, 2)}; distance covered: {round(distance_covered, 2)}; available: {vehicle.is_available}; remaining travel time: {vehicle.remaining_travel_time}")
        return intermediate_lat, intermediate_long, progress


    def refresh_scenario(self, scenario:Scenario) -> List[Vehicle]:
        vehicles_db = self.vehicle_repo.get_by_scenario(self.active_scenario)
        updated_vehicles = []
        updated_customers = []
        for i, db_vehicle in enumerate(vehicles_db):
            scenario_vehicle = [v for v in scenario.vehicles if v.id == db_vehicle.vehicle_id][0]
            # update db entry with scenario data
            db_vehicle.remaining_travel_time = scenario_vehicle.remainingTravelTime if scenario_vehicle.remainingTravelTime is not None else 0
            db_vehicle.vehicle_speed = scenario_vehicle.vehicleSpeed
            db_vehicle.active_time = scenario_vehicle.activeTime
            db_vehicle.distance_travelled = scenario_vehicle.distanceTravelled
            db_vehicle.number_of_trips = scenario_vehicle.numberOfTrips
            db_vehicle.is_available = scenario_vehicle.isAvailable
            if scenario_vehicle.customerId is not None:
                # vehicle is busy, set customer id and change status if needed
                db_vehicle.current_customer_id = scenario_vehicle.customerId
                if db_vehicle.enroute == VehicleRouteStatus.IDLE:
                    db_vehicle.enroute = VehicleRouteStatus.TO_CUSTOMER
            else:
                # Check if there are any active assignments for this vehicle when it has no customer
                active_assignment = self.assignment_repo.get_active_assignment(self.active_scenario, db_vehicle.vehicle_id)
                if active_assignment is not None:
                    # Reassign the customer ID from the active assignment
                    db_vehicle.current_customer_id = active_assignment.customer_id
                    logger.info(f"Reassigned customer {db_vehicle.current_customer_id} to vehicle {db_vehicle.vehicle_id}")
                    if db_vehicle.enroute == VehicleRouteStatus.IDLE:
                        db_vehicle.enroute = VehicleRouteStatus.TO_CUSTOMER
            # now update vehicle if busy
            if db_vehicle.current_customer_id is not None:
                db_customer = self.customer_repo.get(self.active_scenario, db_vehicle.current_customer_id)
                # either the vehicle is going to the customer or to the destination
                if db_vehicle.enroute == VehicleRouteStatus.TO_CUSTOMER:
                    # destination corresponds to the customer's origin
                    target_lat, target_long = db_customer.coord_x, db_customer.coord_y
                else:
                    # destination corresponds to the customer's destination
                    target_lat, target_long = db_customer.destination_x, db_customer.destination_y
                v_curr_lat, v_curr_long, progress = self.calculate_vehicle_position(db_vehicle, target_lat, target_long)
                self.previous_remaining_time_per_vehicle[db_vehicle.vehicle_id] = db_vehicle.remaining_travel_time
                db_vehicle.current_coord_x = v_curr_lat
                db_vehicle.current_coord_y = v_curr_long
                # now we check if the vehicle has reached the destination approximately
                if progress >= 0.97:
                    active_assignment = self.assignment_repo.get_active_assignment(self.active_scenario, db_vehicle.vehicle_id)
                    if db_vehicle.enroute == VehicleRouteStatus.TO_CUSTOMER:
                        # the vehicle has reached the customer
                        logger.info(f"Vehicle {db_vehicle.vehicle_id} has reached the customer")
                        db_vehicle.enroute = VehicleRouteStatus.TO_DESTINATION
                        db_customer.picked_up = True
                        # vehicle is now exactly at the customer, both origin and current are the same
                        db_vehicle.current_coord_x = target_lat
                        db_vehicle.current_coord_y = target_long
                        db_vehicle.coord_x = target_lat 
                        db_vehicle.coord_y = target_long
                    elif db_vehicle.enroute == VehicleRouteStatus.TO_DESTINATION:
                        # the vehicle has reached the destination, i.e. customer has been dropped off
                        logger.info(f"Vehicle {db_vehicle.vehicle_id} has reached the destination")
                        # Set current and origin coordinates
                        db_vehicle.current_coord_x = target_lat
                        db_vehicle.current_coord_y = target_long
                        db_vehicle.coord_x = target_lat 
                        db_vehicle.coord_y = target_long
                        # Customer is now exactly at the destination
                        db_customer.coord_x = db_customer.destination_x
                        db_customer.coord_y = db_customer.destination_y
                        # Also set 
                        db_vehicle.current_customer_id = None
                        db_customer.picked_up = False
                        db_customer.awaiting_service = False
                        # the assignment ends
                        self.assignment_repo.complete(active_assignment.assignment_id, 0.0)
                        time.sleep(0.1)
                        # vehicle is now idle
                        db_vehicle.enroute = VehicleRouteStatus.IDLE
                        # set customer coordinates to make sure now destination and customer are the same
                    else:
                        print("SHOULD NOT HAPPEN")
                    # we delete it because the care made a turn and the time will go up anyhow. Thats fine, because w ejust changes the state of the vehicle, but if we miss this turn, we need to catch up
                    del self.previous_remaining_time_per_vehicle[db_vehicle.vehicle_id]
                # if customer has been picked up customer location will be car's location
                if db_vehicle.enroute == VehicleRouteStatus.TO_DESTINATION:
                    db_customer.coord_x = db_vehicle.current_coord_x
                    db_customer.coord_y = db_vehicle.current_coord_y
                updated_customers.append(db_customer)
            if db_vehicle.vehicle_speed == None:
                db_vehicle.vehicle_speed = 15.0
            updated_vehicles.append(db_vehicle)
        # Batch update vehicles and customers
        self.vehicle_repo.batch_update(updated_vehicles)
        self.customer_repo.batch_update(updated_customers)
        available_vehicles = [v for v in vehicles_db if v.current_customer_id is None]
        return available_vehicles


    def run_scenario(self):
        logger.info(f"Starting scenario with { sum(len(customers) for customers in self.active_assignment.values())} customers and {len(self.active_assignment)} vehicles")
        # make initial assignment
        print(self.active_assignment)
        active_vehicles, active_customers = self.make_initial_assignment()
        # remove assigned customers from assignment and add assignments to db
        self.update_assignment_after_step(active_vehicles, active_customers)
        # scenario run
        while True:
            # the loop exits when all customers have been delivered
            scenario_json = self.runner.get_scenario(self.active_scenario)
            scenario = self.generator.scenario_json_to_dto(scenario_json)
            available_vehicles = self.refresh_scenario(scenario)
            # now we need to check if any vehicles have freed up
            for v in available_vehicles:
                if v.vehicle_id in self.active_assignment and len(self.active_assignment[v.vehicle_id]) > 0:
                    # means the vehicle has freed up and we can assign it its next customer
                    response = self.runner.update_scenario(
                        self.active_scenario,
                        [
                            {
                                "id": v.vehicle_id,
                                "customerId": self.active_assignment[v.vehicle_id][0]
                            }
                        ]
                    )
                    self.update_assignment_after_step(
                        active_vehicles=[v.vehicle_id],
                        active_customers=[self.active_assignment[v.vehicle_id][0]]
                    )
                    time.sleep(3)
            # check if no customers are awaiting service anymore i.e. all assignments have been completed
            all_customers = self.customer_repo.get_by_scenario(self.active_scenario)
            if all(c.awaiting_service == False for c in all_customers):
                logger.info("All customers have been served. Scenario complete.")
                break
            time.sleep(1.5)
        return True


    def call_solver(self, scenario:ScenarioDTO):
        request_body = {
            "id": str(scenario.id),
            "startTime": str(scenario.startTime),
            "endTime": str(scenario.endTime),
            "status": scenario.status,
            "vehicles": [asdict(v) for v in scenario.vehicles] if scenario.vehicles else None,
            "customers": [asdict(c) for c in scenario.customers] if scenario.customers else None
        }
        response = requests.post('http://localhost:5000/solve', json=request_body)
        return response.json()


    