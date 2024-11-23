import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from scenario_generator_client import ScenarioGeneratorClient
from scenario_runner_client import ScenarioRunnerClient, Scenario as RunnerScenario
from database.repositories import ScenarioRepository
from models.scenario import Scenario
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

    def create_and_initialize_scenario(
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
            
            # Convert DTO to Runner's Scenario format
            runner_scenario = RunnerScenario(
                id=str(scenario_dto.id),
                startTime=scenario_dto.startTime,
                endTime=None,
                status="RUNNING",
                customers=scenario_dto.customers,
                vehicles=scenario_dto.vehicles
            )
            
            # Step 2: Initialize scenario in runner
            logger.info(f"Initializing scenario {runner_scenario.id}...")
            success = self.runner.initialize_scenario(runner_scenario)
            
            if not success:
                logger.error("Failed to initialize scenario")
                return None
                
            logger.info(f"Successfully created and initialized scenario {runner_scenario.id}")
            return scenario_dto.id
            
        except Exception as e:
            logger.error(f"Error creating scenario: {str(e)}")
            return None
