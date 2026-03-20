"""Inspection models — 4.10 ПРЕДПИСАНИЯ СДО.

Inspection + InspectionLog (status change history).
"""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import DateTime, Date, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InspectionStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class InspectionEntityType(str, enum.Enum):
    DRAWING = "DRAWING"
    ASBUILT = "ASBUILT"
    ESTIMATE_ITEM = "ESTIMATE_ITEM"


class Inspection(Base):
    __tablename__ = "inspections"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    number: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    norm_reference: Mapped[str | None] = mapped_column(String(500))  # "СП 70.13330.2022 п.5.3"
    planned_fix_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_fix_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[InspectionStatus] = mapped_column(
        Enum(InspectionStatus, name="inspection_status"),
        default=InspectionStatus.OPEN,
    )
    related_entity_type: Mapped[InspectionEntityType | None] = mapped_column(
        Enum(InspectionEntityType, name="inspection_entity_type"),
    )
    related_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Relationships
    project = relationship("Project", back_populates="inspections")
    logs = relationship("InspectionLog", back_populates="inspection", lazy="selectin")


class InspectionLog(Base):
    __tablename__ = "inspection_logs"

    inspection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    old_status: Mapped[InspectionStatus] = mapped_column(
        Enum(InspectionStatus, name="inspection_status", create_type=False), nullable=False
    )
    new_status: Mapped[InspectionStatus] = mapped_column(
        Enum(InspectionStatus, name="inspection_status", create_type=False), nullable=False
    )
    comment: Mapped[str | None] = mapped_column(String(2000))
    changed_by: Mapped[str | None] = mapped_column(String(200))

    # Relationships
    inspection = relationship("Inspection", back_populates="logs")
