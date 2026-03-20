"""Material models — 4.8 ВХОДНОЙ КОНТРОЛЬ + 4.9 ФОРМА М-29.

MaterialCertificate, M29Report, M29Line (with GENERATED COLUMN for deviation).
"""

import enum
import uuid
from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Computed,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CertificateStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class M29Status(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"


# ── 4.8 Сертификат качества материала ────────────────────────────
class MaterialCertificate(Base):
    __tablename__ = "material_certificates"

    specification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("specifications.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    standard: Mapped[str | None] = mapped_column(String(200))  # ГОСТ/ТУ
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[CertificateStatus] = mapped_column(
        Enum(CertificateStatus, name="certificate_status"),
        default=CertificateStatus.PENDING,
    )
    rejection_reason: Mapped[str | None] = mapped_column(String(1000))

    # Relationships
    specification = relationship("Specification", back_populates="material_certificates")


# ── 4.9 Отчёт М-29 ──────────────────────────────────────────────
class M29Report(Base):
    __tablename__ = "m29_reports"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    foreman_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[M29Status] = mapped_column(
        Enum(M29Status, name="m29_status"),
        default=M29Status.DRAFT,
    )

    __table_args__ = (
        CheckConstraint("period_month >= 1 AND period_month <= 12", name="ck_m29_month"),
    )

    # Relationships
    project = relationship("Project", back_populates="m29_reports")
    lines = relationship("M29Line", back_populates="report", lazy="selectin")


# ── 4.9 Строка М-29 (с GENERATED COLUMN deviation) ──────────────
class M29Line(Base):
    __tablename__ = "m29_lines"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("m29_reports.id", ondelete="CASCADE"), nullable=False
    )
    specification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("specifications.id", ondelete="CASCADE"), nullable=False
    )
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    norm_consumption: Mapped[float] = mapped_column(Numeric(18, 4), default=0)
    actual_consumption: Mapped[float] = mapped_column(Numeric(18, 4), default=0)
    deviation: Mapped[float] = mapped_column(
        Numeric(18, 4),
        Computed("actual_consumption - norm_consumption", persisted=True),
    )

    # Relationships
    report = relationship("M29Report", back_populates="lines")
    specification = relationship("Specification")
