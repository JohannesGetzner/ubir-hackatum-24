import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from scenario_generator_client import ScenarioGeneratorClient
from scenario_runner_client import ScenarioRunnerClient, Scenario as RunnerScenario
from database.repositories import ScenarioRepository, VehicleRepository, CustomerRepository
from models.scenario import Scenario
from models.vehicle import Vehicle
from models.customer import Customer
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

    def create_scenario(
        self,
        num_vehicles: Optional[int] = None,
        num_customers: Optional[int] = None
    ) -> Optional[UUID]:
        """
        Create a new scenario, initialize it, and save it to the database.
        
        Args:
            num_vehicles: Optional number of vehicles to include
            num_customers: Optional number of customers to include
            
        Returns:
            UUID of the created scenario if successful, None otherwise
        """
        try:
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
                status=ScenarioStatus.CREATED
            )
            self.scenario_repo.create(db_scenario)

            # Save vehicles to database
            logger.info("Saving vehicles to database...")
            for vehicle_dto in scenario_dto.vehicles:
                vehicle = Vehicle(
                    scenario_id=str(scenario_dto.id),
                    vehicle_id=str(vehicle_dto.id),
                    coord_x=vehicle_dto.coordX,
                    coord_y=vehicle_dto.coordY
                
                )
                self.vehicle_repo.create(vehicle)

            # Save customers to database
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
        except:
            logger.error("Failed to create scenario")
            return None
            

    def initialize_scenario(self, scenario: Scenario) -> bool:
        # Step 2: Initialize scenario in runner
        logger.info(f"Initializing scenario {scenario.id}...")
        try:
            success = self.runner.initialize_scenario(scenario)
            logger.info(f"Successfully created and initialized scenario {scenario.id}")
            return True
        except:
            logger.error(f"Failed to initialize scenario {scenario.id}")
            return False


    def launch_scenario(self, scenario_id:str, speed:float):
        # Step 3: Launch scenario
        logger.info(f"Launching scenario {scenario_id}")
        try:
            success = self.runner.launch_scenario(scenario_id=scenario_id,speed=speed)
            self.scenario_repo.update(Scenario(scenario_id=scenario_id, status=ScenarioStatus.RUNNING))
            logger.info(f"Successfully launched scenario")
            return True
        except:
            logger.error(f"Failed to launch scenario with id {scenario_id}")
            return False
            
       
