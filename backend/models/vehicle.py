import random
from typing import Optional, List
from uuid import UUID
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Boolean, Integer, ForeignKey, Enum as SQLEnum, UniqueConstraint

from .base import Base

class VehicleRouteStatus(str, Enum):
    IDLE = "idle"
    TO_CUSTOMER = "cust"
    TO_DESTINATION = "dest"

def get_random_car():
    car_names = ["Tesla Model 3", "Tesla Model S", "Tesla Model Y", "Nissan Leaf", "Ford Mustang Mach-E", "Audi e-tron", "Jaguar I-PACE", "Porsche Taycan"]
    return random.choice(car_names)

class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint('vehicle_id', name='uq_vehicle_id'),
    )

    scenario_id: Mapped[UUID] = mapped_column(String, ForeignKey("scenarios.scenario_id"), primary_key=True)
    vehicle_id: Mapped[UUID] = mapped_column(String, primary_key=True)
    vehicle_name: Mapped[str] = mapped_column(String, nullable=True, default=get_random_car())
    active_time: Mapped[float] = mapped_column(Float, default=0.0)
    coord_x: Mapped[float] = mapped_column(Float, default=0.0)
    coord_y: Mapped[float] = mapped_column(Float, default=0.0)
    current_coord_x: Mapped[float] = mapped_column(Float, default=0.0)
    current_coord_y: Mapped[float] = mapped_column(Float, default=0.0)
    current_customer_id: Mapped[Optional[UUID]] = mapped_column(String, ForeignKey("customers.customer_id"), nullable=True)
    distance_travelled: Mapped[float] = mapped_column(Float, default=0.0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    number_of_trips: Mapped[int] = mapped_column(Integer, default=0)
    remaining_travel_time: Mapped[float] = mapped_column(Float, default=0.0)
    vehicle_speed: Mapped[float] = mapped_column(Float, default=1.0)
    enroute: Mapped[VehicleRouteStatus] = mapped_column(SQLEnum(VehicleRouteStatus), default=VehicleRouteStatus.IDLE)

    # Relationships
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="vehicles")
    current_customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="assigned_vehicle")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="vehicle")

    def to_dict(self) -> dict:
        """Convert Vehicle instance to a dictionary for map visualization."""
        return {
            'vehicle_id': str(self.vehicle_id),
            'id': str(self.vehicle_id),
            'scenario_id': str(self.scenario_id),
            'vehicle_name': str(get_random_car()),
            'latitude': self.current_coord_x,
            'longitude': self.current_coord_y,
            'is_available': self.is_available,
            'current_customer_id': str(self.current_customer_id) if self.current_customer_id else None,
            'number_of_trips': self.number_of_trips,
            'remaining_travel_time': self.remaining_travel_time,
            'vehicle_speed': self.vehicle_speed,
            'distance_travelled': self.distance_travelled,
            'active_time': self.active_time,
            'enroute': self.enroute.value
        }