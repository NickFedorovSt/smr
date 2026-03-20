"""Pydantic v2 schemas for Contracts (Income / Expense) + distribution links."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.contracts.models import ContractStatus


# ══════════════════════════════════════════════════════════════════
# IncomeContract
# ══════════════════════════════════════════════════════════════════
class IncomeContractCreate(BaseModel):
    project_id: UUID
    number: str
    name: str
    counterparty: str
    total_amount: Decimal = Decimal("0")
    start_date: date | None = None
    end_date: date | None = None
    status: ContractStatus = ContractStatus.DRAFT


class IncomeContractUpdate(BaseModel):
    number: str | None = None
    name: str | None = None
    counterparty: str | None = None
    total_amount: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: ContractStatus | None = None


class IncomeContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    number: str
    name: str
    counterparty: str
    total_amount: Decimal
    start_date: date | None
    end_date: date | None
    status: ContractStatus
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# ExpenseContract
# ══════════════════════════════════════════════════════════════════
class ExpenseContractCreate(BaseModel):
    project_id: UUID
    number: str
    name: str
    counterparty: str
    total_amount: Decimal = Decimal("0")
    start_date: date | None = None
    end_date: date | None = None
    status: ContractStatus = ContractStatus.DRAFT


class ExpenseContractUpdate(BaseModel):
    number: str | None = None
    name: str | None = None
    counterparty: str | None = None
    total_amount: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: ContractStatus | None = None


class ExpenseContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    number: str
    name: str
    counterparty: str
    total_amount: Decimal
    start_date: date | None
    end_date: date | None
    status: ContractStatus
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# Distribution links (ЛС ↔ IncomeContract, Income ↔ Expense)
# ══════════════════════════════════════════════════════════════════
class LsIncomeContractCreate(BaseModel):
    ls_id: UUID
    income_contract_id: UUID
    percentage: Decimal

    @field_validator("percentage")
    @classmethod
    def validate_percentage(cls, v: Decimal) -> Decimal:
        if v < 0 or v > 100:
            raise ValueError("Процент должен быть от 0 до 100")
        return v


class LsIncomeContractRead(BaseModel):
    ls_id: UUID
    income_contract_id: UUID
    percentage: Decimal


class IncomeExpenseContractCreate(BaseModel):
    income_contract_id: UUID
    expense_contract_id: UUID
    percentage: Decimal

    @field_validator("percentage")
    @classmethod
    def validate_percentage(cls, v: Decimal) -> Decimal:
        if v < 0 or v > 100:
            raise ValueError("Процент должен быть от 0 до 100")
        return v


class IncomeExpenseContractRead(BaseModel):
    income_contract_id: UUID
    expense_contract_id: UUID
    percentage: Decimal
