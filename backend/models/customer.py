import random
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Boolean, ForeignKey

from .base import Base

def get_random_name():
    first_names = ["Alice", "Bob", "Carol", "David", "Eve"]
    return random.choice(first_names)


class Customer(Base):
    __tablename__ = "customers"

    scenario_id: Mapped[UUID] = mapped_column(String, ForeignKey("scenarios.scenario_id"), primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(String, primary_key=True)
    fake_name: Mapped[str] = mapped_column(String, nullable=True, default=get_random_name())
    awaiting_service: Mapped[bool] = mapped_column(Boolean, default=False)
    picked_up: Mapped[bool] = mapped_column(Boolean, default=False)
    coord_x: Mapped[float] = mapped_column(Float, default=0.0)
    coord_y: Mapped[float] = mapped_column(Float, default=0.0)
    destination_x: Mapped[float] = mapped_column(Float, default=0.0)
    destination_y: Mapped[float] = mapped_column(Float, default=0.0)
    waiting_time: Mapped[float] = mapped_column(Float, default=0.0)
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="customers")
    assigned_vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="current_customer")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="customer")

    def to_dict(self) -> dict:
        """Convert Customer instance to a dictionary for map visualization."""
        return {
            'id': str(self.customer_id),
            'scenario_id': str(self.scenario_id),
            'fake_name': str(get_random_name()),
            'latitude': self.coord_x,
            'longitude': self.coord_y,
            'destination_longitude': self.destination_x,
            'destination_latitude': self.destination_y,
            'awaiting_service': self.awaiting_service,
            'picked_up': self.picked_up,
            'waiting_time': self.waiting_time,
            'priority_score': self.priority_score,
            'assigned_vehicle_id': str(self.assigned_vehicle.vehicle_id) if self.assigned_vehicle else None
        }
