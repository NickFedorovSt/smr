"""Repository for Contracts — CRUD + distribution validation.

Key feature: SUM(percentage) ≤ 100 validation for ЛС ↔ IncomeContract (Раздел 6.5).
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, delete, func, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contracts.models import (
    IncomeContract,
    ExpenseContract,
    ls_income_contract,
    income_expense_contract,
)
from app.modules.contracts.schemas import (
    IncomeContractCreate, IncomeContractUpdate,
    ExpenseContractCreate, ExpenseContractUpdate,
    LsIncomeContractCreate,
    IncomeExpenseContractCreate,
)


class IncomeContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, project_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[IncomeContract]:
        stmt = select(IncomeContract)
        if project_id:
            stmt = stmt.where(IncomeContract.project_id == project_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, contract_id: UUID) -> IncomeContract | None:
        result = await self.session.execute(
            select(IncomeContract).where(IncomeContract.id == contract_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: IncomeContractCreate) -> IncomeContract:
        contract = IncomeContract(**data.model_dump())
        self.session.add(contract)
        await self.session.flush()
        return contract

    async def update(self, contract_id: UUID, data: IncomeContractUpdate) -> IncomeContract | None:
        contract = await self.get_by_id(contract_id)
        if not contract:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(contract, field, value)
        await self.session.flush()
        return contract

    async def delete(self, contract_id: UUID) -> bool:
        result = await self.session.execute(
            delete(IncomeContract).where(IncomeContract.id == contract_id)
        )
        return result.rowcount > 0


class ExpenseContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, project_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[ExpenseContract]:
        stmt = select(ExpenseContract)
        if project_id:
            stmt = stmt.where(ExpenseContract.project_id == project_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, contract_id: UUID) -> ExpenseContract | None:
        result = await self.session.execute(
            select(ExpenseContract).where(ExpenseContract.id == contract_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ExpenseContractCreate) -> ExpenseContract:
        contract = ExpenseContract(**data.model_dump())
        self.session.add(contract)
        await self.session.flush()
        return contract

    async def update(self, contract_id: UUID, data: ExpenseContractUpdate) -> ExpenseContract | None:
        contract = await self.get_by_id(contract_id)
        if not contract:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(contract, field, value)
        await self.session.flush()
        return contract

    async def delete(self, contract_id: UUID) -> bool:
        result = await self.session.execute(
            delete(ExpenseContract).where(ExpenseContract.id == contract_id)
        )
        return result.rowcount > 0


class ContractDistributionRepository:
    """Distribution links management with SUM(percentage) ≤ 100 validation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── ЛС ↔ IncomeContract ─────────────────────────────────────
    async def get_ls_income_sum(self, ls_id: UUID) -> Decimal:
        """Get current SUM(percentage) for a given ЛС across all income contracts."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(ls_income_contract.c.percentage), 0))
            .where(ls_income_contract.c.ls_id == ls_id)
        )
        return Decimal(str(result.scalar()))

    async def add_ls_income(self, data: LsIncomeContractCreate) -> None:
        """Add ЛС ↔ IncomeContract link.

        Validates SUM(percentage) by ls_id ≤ 100 before insert (Раздел 6.5).
        Raises ValueError if exceeded.
        """
        current_sum = await self.get_ls_income_sum(data.ls_id)
        if current_sum + data.percentage > 100:
            raise ValueError(
                f"Суммарный процент распределения по ЛС превышает 100% "
                f"(текущий: {current_sum}%, добавляемый: {data.percentage}%)"
            )
        await self.session.execute(
            insert(ls_income_contract).values(
                ls_id=data.ls_id,
                income_contract_id=data.income_contract_id,
                percentage=data.percentage,
            )
        )
        await self.session.flush()

    async def remove_ls_income(self, ls_id: UUID, income_contract_id: UUID) -> bool:
        result = await self.session.execute(
            delete(ls_income_contract).where(
                ls_income_contract.c.ls_id == ls_id,
                ls_income_contract.c.income_contract_id == income_contract_id,
            )
        )
        return result.rowcount > 0

    async def get_ls_income_links(self, ls_id: UUID) -> list[dict]:
        result = await self.session.execute(
            select(ls_income_contract).where(ls_income_contract.c.ls_id == ls_id)
        )
        return [dict(row._mapping) for row in result]

    # ── IncomeContract ↔ ExpenseContract ─────────────────────────
    async def get_income_expense_sum(self, income_contract_id: UUID) -> Decimal:
        result = await self.session.execute(
            select(func.coalesce(func.sum(income_expense_contract.c.percentage), 0))
            .where(income_expense_contract.c.income_contract_id == income_contract_id)
        )
        return Decimal(str(result.scalar()))

    async def add_income_expense(self, data: IncomeExpenseContractCreate) -> None:
        current_sum = await self.get_income_expense_sum(data.income_contract_id)
        if current_sum + data.percentage > 100:
            raise ValueError(
                f"Суммарный процент распределения по доходному договору превышает 100% "
                f"(текущий: {current_sum}%, добавляемый: {data.percentage}%)"
            )
        await self.session.execute(
            insert(income_expense_contract).values(
                income_contract_id=data.income_contract_id,
                expense_contract_id=data.expense_contract_id,
                percentage=data.percentage,
            )
        )
        await self.session.flush()

    async def remove_income_expense(self, income_contract_id: UUID, expense_contract_id: UUID) -> bool:
        result = await self.session.execute(
            delete(income_expense_contract).where(
                income_expense_contract.c.income_contract_id == income_contract_id,
                income_expense_contract.c.expense_contract_id == expense_contract_id,
            )
        )
        return result.rowcount > 0

    async def get_income_expense_links(self, income_contract_id: UUID) -> list[dict]:
        result = await self.session.execute(
            select(income_expense_contract)
            .where(income_expense_contract.c.income_contract_id == income_contract_id)
        )
        return [dict(row._mapping) for row in result]
