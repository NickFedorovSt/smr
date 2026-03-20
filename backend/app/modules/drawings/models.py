"""Drawing & Specification models — 4.4 РАБОЧАЯ ДОКУМЕНТАЦИЯ."""

import enum
import uuid

from sqlalchemy import Column, Enum, ForeignKey, Numeric, String, Table, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DrawingStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    REVISION = "REVISION"
    CANCELLED = "CANCELLED"


# ── Association: ЛС ↔ Drawing (многие ко многим) ─────────────────
ls_drawing = Table(
    "ls_drawing",
    Base.metadata,
    Column("ls_id", UUID(as_uuid=True), ForeignKey("local_estimates.id", ondelete="CASCADE"), primary_key=True),
    Column("drawing_id", UUID(as_uuid=True), ForeignKey("drawings.id", ondelete="CASCADE"), primary_key=True),
)


class Drawing(Base):
    __tablename__ = "drawings"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    mark: Mapped[str] = mapped_column(String(20), nullable=False)  # КЖ, АР, ЭОМ, ОВ, ВК, ТХ
    sheet_number: Mapped[str] = mapped_column(String(50), nullable=False)
    revision: Mapped[str] = mapped_column(String(10), default="0")
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DrawingStatus] = mapped_column(
        Enum(DrawingStatus, name="drawing_status"),
        default=DrawingStatus.DRAFT,
    )
    issued_date = mapped_column(Date, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="drawings")
    specifications = relationship("Specification", back_populates="drawing", lazy="selectin")
    local_estimates = relationship(
        "LocalEstimate",
        secondary=ls_drawing,
        backref="drawings",
        lazy="selectin",
    )


class Specification(Base):
    __tablename__ = "specifications"

    drawing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drawings.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    mark_standard: Mapped[str | None] = mapped_column(String(200))  # ГОСТ/ТУ
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    volume_designed: Mapped[float] = mapped_column(Numeric(18, 4), default=0)

    # Relationships
    drawing = relationship("Drawing", back_populates="specifications")
    material_certificates = relationship("MaterialCertificate", back_populates="specification", lazy="selectin")
