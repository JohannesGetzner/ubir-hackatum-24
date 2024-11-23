from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Boolean, ForeignKey

from .base import Base

class Customer(Base):
    __tablename__ = "customers"

    scenario_id: Mapped[UUID] = mapped_column(String, ForeignKey("scenarios.scenario_id"), primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(String, primary_key=True)
    awaiting_service: Mapped[bool] = mapped_column(Boolean, default=False)
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
