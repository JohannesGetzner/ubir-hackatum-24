from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, Enum as SQLAEnum, Integer

from .base import Base, ScenarioStatus

class Scenario(Base):
    __tablename__ = "scenarios"

    scenario_id: Mapped[UUID] = mapped_column(String, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[ScenarioStatus] = mapped_column(
        SQLAEnum(ScenarioStatus),
        default=ScenarioStatus.RUNNING,
        nullable=False
    )
    efficiency_setting: Mapped[float] = mapped_column(Float, default=1.0)
    sustainability_setting: Mapped[float] = mapped_column(Float, default=1.0)
    satisfaction_setting: Mapped[float] = mapped_column(Float, default=1.0)
    num_customers: Mapped[float] = mapped_column(Integer, nullable=False)
    num_vehicles: Mapped[float] = mapped_column(Integer, nullable=False)

    # Relationships
    customers: Mapped[List["Customer"]] = relationship("Customer", back_populates="scenario", cascade="all, delete-orphan")
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="scenario", cascade="all, delete-orphan")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="scenario", cascade="all, delete-orphan")
