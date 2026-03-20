"""As-built documentation models — 4.7 ИСПОЛНИТЕЛЬНАЯ ДОКУМЕНТАЦИЯ.

AsBuiltDoc (АОСР/АООК), WorkJournal (ОЖР), JournalEntry.
"""

import enum
import uuid
from datetime import date

from sqlalchemy import Column, Date, Enum, ForeignKey, Numeric, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AsBuiltType(str, enum.Enum):
    AOSR = "AOSR"
    AOOK = "AOOK"
    EXEC_SCHEME = "EXEC_SCHEME"


class AsBuiltStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SIGNED = "SIGNED"
    ACCEPTED = "ACCEPTED"


class JournalType(str, enum.Enum):
    GENERAL = "GENERAL"
    SPECIAL = "SPECIAL"


# ── Association: AsBuiltDoc ↔ Drawing ────────────────────────────
asbuilt_drawing = Table(
    "asbuilt_drawing",
    Base.metadata,
    Column("asbuilt_id", UUID(as_uuid=True), ForeignKey("asbuilt_docs.id", ondelete="CASCADE"), primary_key=True),
    Column("drawing_id", UUID(as_uuid=True), ForeignKey("drawings.id", ondelete="CASCADE"), primary_key=True),
)

# ── Association: AsBuiltDoc ↔ Specification (с объёмом закрытия) ──
asbuilt_specification = Table(
    "asbuilt_specification",
    Base.metadata,
    Column("asbuilt_id", UUID(as_uuid=True), ForeignKey("asbuilt_docs.id", ondelete="CASCADE"), primary_key=True),
    Column("specification_id", UUID(as_uuid=True), ForeignKey("specifications.id", ondelete="CASCADE"), primary_key=True),
    Column("volume_closed", Numeric(18, 4), nullable=False, default=0),
)


class AsBuiltDoc(Base):
    __tablename__ = "asbuilt_docs"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[AsBuiltType] = mapped_column(
        Enum(AsBuiltType, name="asbuilt_type"), nullable=False
    )
    number: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    sign_date: Mapped[date] = mapped_column(Date, nullable=False)
    foreman: Mapped[str] = mapped_column(String(200), nullable=False)
    supervisor: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[AsBuiltStatus] = mapped_column(
        Enum(AsBuiltStatus, name="asbuilt_status"),
        default=AsBuiltStatus.DRAFT,
    )

    # Relationships
    project = relationship("Project", back_populates="asbuilt_docs")
    drawings = relationship("Drawing", secondary=asbuilt_drawing, lazy="selectin")
    specifications = relationship("Specification", secondary=asbuilt_specification, lazy="selectin")


class WorkJournal(Base):
    __tablename__ = "work_journals"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[JournalType] = mapped_column(
        Enum(JournalType, name="journal_type"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    started_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="work_journals")
    entries = relationship("JournalEntry", back_populates="journal", lazy="selectin")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    journal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_journals.id", ondelete="CASCADE"), nullable=False
    )
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    responsible: Mapped[str] = mapped_column(String(200), nullable=False)

    # Relationships
    journal = relationship("WorkJournal", back_populates="entries")
