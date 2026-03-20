"""Contract models — 4.3 ДОГОВОРНАЯ СИСТЕМА.

Distribution level: ЛС → Contract (NOT EstimateItem → Contract).
"""

import enum
import uuid
from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContractStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


# ── Association: ЛС ↔ IncomeContract (многие ко многим) ──────────
ls_income_contract = Table(
    "ls_income_contract",
    Base.metadata,
    Column("ls_id", UUID(as_uuid=True), ForeignKey("local_estimates.id", ondelete="CASCADE"), primary_key=True),
    Column("income_contract_id", UUID(as_uuid=True), ForeignKey("income_contracts.id", ondelete="CASCADE"), primary_key=True),
    Column("percentage", Numeric(5, 2), nullable=False),
    CheckConstraint("percentage >= 0 AND percentage <= 100", name="ck_ls_income_percentage"),
)

# ── Association: IncomeContract ↔ ExpenseContract (многие ко многим)
income_expense_contract = Table(
    "income_expense_contract",
    Base.metadata,
    Column("income_contract_id", UUID(as_uuid=True), ForeignKey("income_contracts.id", ondelete="CASCADE"), primary_key=True),
    Column("expense_contract_id", UUID(as_uuid=True), ForeignKey("expense_contracts.id", ondelete="CASCADE"), primary_key=True),
    Column("percentage", Numeric(5, 2), nullable=False),
    CheckConstraint("percentage >= 0 AND percentage <= 100", name="ck_income_expense_percentage"),
)


# ── Доходный договор с Заказчиком ────────────────────────────────
class IncomeContract(Base):
    __tablename__ = "income_contracts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    number: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    counterparty: Mapped[str] = mapped_column(String(500), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, name="contract_status"),
        default=ContractStatus.DRAFT,
    )

    # Relationships
    project = relationship("Project", back_populates="income_contracts")
    local_estimates = relationship(
        "LocalEstimate",
        secondary=ls_income_contract,
        backref="income_contracts",
        lazy="selectin",
    )
    expense_contracts = relationship(
        "ExpenseContract",
        secondary=income_expense_contract,
        backref="income_contracts",
        lazy="selectin",
    )


# ── Расходный договор с Субподрядчиком ───────────────────────────
class ExpenseContract(Base):
    __tablename__ = "expense_contracts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    number: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    counterparty: Mapped[str] = mapped_column(String(500), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, name="contract_status", create_type=False),
        default=ContractStatus.DRAFT,
    )

    # Relationships
    project = relationship("Project", back_populates="expense_contracts")
