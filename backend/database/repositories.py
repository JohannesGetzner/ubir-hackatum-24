from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import (
    Customer,
    Scenario,
    ScenarioStatus,
    Vehicle,
    Assignment,
    AssignmentStatus
)

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get(self, scenario_id: UUID, customer_id: UUID) -> Optional[Customer]:
        return self.db.get(Customer, {"scenario_id": scenario_id, "customer_id": customer_id})

    def get_by_scenario(self, scenario_id: UUID) -> List[Customer]:
        stmt = select(Customer).where(Customer.scenario_id == scenario_id)
        return list(self.db.scalars(stmt))

    def get_waiting(self, scenario_id: UUID) -> List[Customer]:
        stmt = select(Customer).where(
            Customer.scenario_id == scenario_id,
            Customer.awaiting_service == True
        )
        return list(self.db.scalars(stmt))

    def update(self, customer: Customer) -> Customer:
        self.db.merge(customer)
        self.db.commit()
        return customer

class ScenarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, scenario: Scenario) -> Scenario:
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def get(self, scenario_id: UUID) -> Optional[Scenario]:
        return self.db.get(Scenario, scenario_id)

    def get_active(self) -> List[Scenario]:
        stmt = select(Scenario).where(Scenario.status == ScenarioStatus.RUNNING)
        return list(self.db.scalars(stmt))

    def update(self, scenario: Scenario) -> Scenario:
        self.db.merge(scenario)
        self.db.commit()
        return scenario

    def finish(self, scenario_id: UUID) -> Optional[Scenario]:
        scenario = self.get(scenario_id)
        if scenario:
            scenario.status = ScenarioStatus.FINISHED
            scenario.end_time = datetime.now()
            self.db.commit()
        return scenario

class VehicleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, vehicle: Vehicle) -> Vehicle:
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle

    def get(self, scenario_id: UUID, vehicle_id: UUID) -> Optional[Vehicle]:
        return self.db.get(Vehicle, {"scenario_id": scenario_id, "vehicle_id": vehicle_id})

    def get_by_scenario(self, scenario_id: UUID) -> List[Vehicle]:
        stmt = select(Vehicle).where(Vehicle.scenario_id == scenario_id)
        return list(self.db.scalars(stmt))

    def get_available(self, scenario_id: UUID) -> List[Vehicle]:
        stmt = select(Vehicle).where(
            Vehicle.scenario_id == scenario_id,
            Vehicle.is_available == True
        )
        return list(self.db.scalars(stmt))

    def update(self, vehicle: Vehicle) -> Vehicle:
        self.db.merge(vehicle)
        self.db.commit()
        return vehicle

    def assign_customer(self, vehicle: Vehicle, customer: Customer) -> Vehicle:
        vehicle.current_customer_id = customer.customer_id
        vehicle.is_available = False
        vehicle.number_of_trips += 1
        self.db.commit()
        return vehicle

    def complete_trip(self, vehicle: Vehicle) -> Vehicle:
        vehicle.current_customer_id = None
        vehicle.is_available = True
        vehicle.remaining_travel_time = 0
        self.db.commit()
        return vehicle

class AssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, assignment: Assignment) -> Assignment:
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get(self, assignment_id: UUID) -> Optional[Assignment]:
        return self.db.get(Assignment, assignment_id)

    def get_by_scenario(self, scenario_id: UUID) -> List[Assignment]:
        stmt = select(Assignment).where(Assignment.scenario_id == scenario_id)
        return list(self.db.scalars(stmt))

    def get_by_vehicle(self, scenario_id: UUID, vehicle_id: UUID) -> List[Assignment]:
        stmt = select(Assignment).where(
            Assignment.scenario_id == scenario_id,
            Assignment.vehicle_id == vehicle_id
        )
        return list(self.db.scalars(stmt))

    def get_by_customer(self, scenario_id: UUID, customer_id: UUID) -> List[Assignment]:
        stmt = select(Assignment).where(
            Assignment.scenario_id == scenario_id,
            Assignment.customer_id == customer_id
        )
        return list(self.db.scalars(stmt))

    def get_active(self, scenario_id: UUID) -> List[Assignment]:
        stmt = select(Assignment).where(
            Assignment.scenario_id == scenario_id,
            Assignment.status == AssignmentStatus.IN_PROGRESS
        )
        return list(self.db.scalars(stmt))

    def get_active_assignment(self, scenario_id: UUID, vehicle_id: UUID) -> Optional[Assignment]:
        stmt = select(Assignment).where(
            Assignment.scenario_id == scenario_id,
            Assignment.vehicle_id == vehicle_id,
            Assignment.status == AssignmentStatus.IN_PROGRESS
        )
        return self.db.scalar(stmt)

    def update(self, assignment: Assignment) -> Assignment:
        self.db.merge(assignment)
        self.db.commit()
        return assignment

    def complete(self, assignment_id: UUID, distance_travelled: float) -> Optional[Assignment]:
        assignment = self.get(assignment_id)
        if assignment:
            assignment.status = AssignmentStatus.COMPLETED
            assignment.assignment_end_time = datetime.now()
            assignment.distance_travelled = distance_travelled
            self.db.commit()
        return assignment

    def cancel(self, assignment_id: UUID) -> Optional[Assignment]:
        assignment = self.get(assignment_id)
        if assignment:
            assignment.status = AssignmentStatus.CANCELLED
            assignment.assignment_end_time = datetime.now()
            self.db.commit()
        return assignment
