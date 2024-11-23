from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, Enum as SQLAEnum, ForeignKey

from .base import Base, AssignmentStatus

class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id: Mapped[UUID] = mapped_column(String, primary_key=True)
    scenario_id: Mapped[UUID] = mapped_column(String, ForeignKey("scenarios.scenario_id"))
    vehicle_id: Mapped[UUID] = mapped_column(String, ForeignKey("vehicles.vehicle_id"))
    customer_id: Mapped[UUID] = mapped_column(String, ForeignKey("customers.customer_id"))
    assignment_start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    assignment_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    distance_travelled: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[AssignmentStatus] = mapped_column(
        SQLAEnum(AssignmentStatus),
        default=AssignmentStatus.IN_PROGRESS,
        nullable=False
    )

    # Relationships
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="assignments")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="assignments")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="assignments")
