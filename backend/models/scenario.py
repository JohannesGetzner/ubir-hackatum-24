from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, Enum as SQLAEnum, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, ScenarioStatus

class Scenario(Base):
    __tablename__ = "scenarios"

    scenario_id: Mapped[str] = mapped_column(String, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[ScenarioStatus] = mapped_column(
        SQLAEnum(ScenarioStatus),
        default=ScenarioStatus.RUNNING,
        nullable=False
    )
    num_customers: Mapped[float] = mapped_column(Integer, nullable=False)
    num_vehicles: Mapped[float] = mapped_column(Integer, nullable=False)

    # Relationships
    customers: Mapped[List["Customer"]] = relationship("Customer", back_populates="scenario", cascade="all, delete-orphan")
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="scenario", cascade="all, delete-orphan")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="scenario", cascade="all, delete-orphan")
    savings_km_genetic: Mapped[float] = mapped_column(Float, default=0.0)
    savings_km_greedy: Mapped[float] = mapped_column(Float, default=0.0)
    savings_time_genetic: Mapped[float] = mapped_column(Float, default=0.0)
    savings_time_greedy: Mapped[float] = mapped_column(Float, default=0.0)

    def to_dict(self):
        return {
            "scenario_id": str(self.scenario_id),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "num_customers": self.num_customers,
            "num_vehicles": self.num_vehicles,
            "savings_km_genetic": self.savings_km_genetic,
            "savings_km_greedy": self.savings_km_greedy,
            "savings_time_genetic": self.savings_time_genetic,
            "savings_time_greedy": self.savings_time_greedy,
        }
