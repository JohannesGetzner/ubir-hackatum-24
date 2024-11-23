from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Boolean, Integer, ForeignKey

from .base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    scenario_id: Mapped[UUID] = mapped_column(String, ForeignKey("scenarios.scenario_id"), primary_key=True)
    vehicle_id: Mapped[UUID] = mapped_column(String, primary_key=True)
    active_time: Mapped[float] = mapped_column(Float, default=0.0)
    coord_x: Mapped[float] = mapped_column(Float, default=0.0)
    coord_y: Mapped[float] = mapped_column(Float, default=0.0)
    current_customer_id: Mapped[Optional[UUID]] = mapped_column(String, ForeignKey("customers.customer_id"), nullable=True)
    distance_travelled: Mapped[float] = mapped_column(Float, default=0.0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    number_of_trips: Mapped[int] = mapped_column(Integer, default=0)
    remaining_travel_time: Mapped[float] = mapped_column(Float, default=0.0)
    vehicle_speed: Mapped[float] = mapped_column(Float, default=1.0)

    # Relationships
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="vehicles")
    current_customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="assigned_vehicle")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="vehicle")
