"""Project model — 4.1 ПРОЕКТ."""

import enum
from datetime import date

from sqlalchemy import Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProjectStatus(str, enum.Enum):
    DESIGN = "DESIGN"
    CONSTRUCTION = "CONSTRUCTION"
    COMMISSIONING = "COMMISSIONING"
    COMPLETED = "COMPLETED"


class Project(Base):
    __tablename__ = "projects"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    customer: Mapped[str | None] = mapped_column(String(500))
    contractor: Mapped[str | None] = mapped_column(String(500))
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_end: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_end: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        default=ProjectStatus.DESIGN,
    )

    # Relationships
    summary_estimates = relationship("SummaryEstimate", back_populates="project", lazy="selectin")
    income_contracts = relationship("IncomeContract", back_populates="project", lazy="selectin")
    expense_contracts = relationship("ExpenseContract", back_populates="project", lazy="selectin")
    drawings = relationship("Drawing", back_populates="project", lazy="selectin")
    asbuilt_docs = relationship("AsBuiltDoc", back_populates="project", lazy="selectin")
    work_journals = relationship("WorkJournal", back_populates="project", lazy="selectin")
    m29_reports = relationship("M29Report", back_populates="project", lazy="selectin")
    inspections = relationship("Inspection", back_populates="project", lazy="selectin")
