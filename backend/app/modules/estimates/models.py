"""Estimate hierarchy models — 4.2 ИЕРАРХИЯ СМЕТНОЙ ДОКУМЕНТАЦИИ (МДС 81-35.2004).

Hierarchy: Project → ССР → ОСР → ЛСР → ЛС → EstimateItem
"""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ExpertiseStatus(str, enum.Enum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REVISION_REQUIRED = "REVISION_REQUIRED"


class LocalEstimateType(str, enum.Enum):
    MAIN = "MAIN"
    ADDITIONAL = "ADDITIONAL"


# ── ССР — Сводный сметный расчёт ────────────────────────────────
class SummaryEstimate(Base):
    __tablename__ = "summary_estimates"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    expertise_status: Mapped[ExpertiseStatus] = mapped_column(
        Enum(ExpertiseStatus, name="expertise_status"),
        default=ExpertiseStatus.NOT_SUBMITTED,
    )
    expertise_date = mapped_column(type_=__import__("sqlalchemy").Date, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="summary_estimates")
    object_estimates = relationship("ObjectEstimate", back_populates="summary_estimate", lazy="selectin")


# ── ОСР — Объектный сметный расчёт ──────────────────────────────
class ObjectEstimate(Base):
    __tablename__ = "object_estimates"

    summary_estimate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("summary_estimates.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    expertise_status: Mapped[ExpertiseStatus] = mapped_column(
        Enum(ExpertiseStatus, name="expertise_status", create_type=False),
        default=ExpertiseStatus.NOT_SUBMITTED,
    )

    # Relationships
    summary_estimate = relationship("SummaryEstimate", back_populates="object_estimates")
    local_estimate_bases = relationship("LocalEstimateBase", back_populates="object_estimate", lazy="selectin")


# ── ЛСР — Локальный сметный расчёт (проектная смета) ─────────────
class LocalEstimateBase(Base):
    __tablename__ = "local_estimate_bases"

    object_estimate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("object_estimates.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    price_index: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    expertise_status: Mapped[ExpertiseStatus] = mapped_column(
        Enum(ExpertiseStatus, name="expertise_status", create_type=False),
        default=ExpertiseStatus.NOT_SUBMITTED,
    )

    # Relationships
    object_estimate = relationship("ObjectEstimate", back_populates="local_estimate_bases")
    local_estimates = relationship("LocalEstimate", back_populates="local_estimate_base", lazy="selectin")


# ── ЛС — Локальная смета (рабочая) ──────────────────────────────
class LocalEstimate(Base):
    __tablename__ = "local_estimates"

    lsr_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("local_estimate_bases.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[LocalEstimateType] = mapped_column(
        Enum(LocalEstimateType, name="local_estimate_type"),
        default=LocalEstimateType.MAIN,
    )
    total_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    price_index: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)

    # Relationships
    local_estimate_base = relationship("LocalEstimateBase", back_populates="local_estimates")
    estimate_items = relationship("EstimateItem", back_populates="local_estimate", lazy="selectin")


# ── Сметная статья ───────────────────────────────────────────────
class EstimateItem(Base):
    __tablename__ = "estimate_items"

    ls_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("local_estimates.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    volume_approved: Mapped[float] = mapped_column(Numeric(18, 4), default=0)
    amount_approved: Mapped[float] = mapped_column(Numeric(18, 2), default=0)

    # Relationships
    local_estimate = relationship("LocalEstimate", back_populates="estimate_items")
    progress_entries = relationship("Progress", back_populates="estimate_item", lazy="selectin")
