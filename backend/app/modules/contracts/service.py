"""Service layer for Contracts — CRUD + distribution with validation."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contracts.repository import (
    IncomeContractRepository,
    ExpenseContractRepository,
    ContractDistributionRepository,
)
from app.modules.contracts.schemas import (
    IncomeContractCreate, IncomeContractUpdate,
    ExpenseContractCreate, ExpenseContractUpdate,
    LsIncomeContractCreate,
    IncomeExpenseContractCreate,
)


class IncomeContractService:
    def __init__(self, session: AsyncSession):
        self.repo = IncomeContractRepository(session)

    async def get_all(self, project_id: UUID | None = None):
        return await self.repo.get_all(project_id=project_id)

    async def get_by_id(self, contract_id: UUID):
        return await self.repo.get_by_id(contract_id)

    async def create(self, data: IncomeContractCreate):
        return await self.repo.create(data)

    async def update(self, contract_id: UUID, data: IncomeContractUpdate):
        return await self.repo.update(contract_id, data)

    async def delete(self, contract_id: UUID):
        return await self.repo.delete(contract_id)


class ExpenseContractService:
    def __init__(self, session: AsyncSession):
        self.repo = ExpenseContractRepository(session)

    async def get_all(self, project_id: UUID | None = None):
        return await self.repo.get_all(project_id=project_id)

    async def get_by_id(self, contract_id: UUID):
        return await self.repo.get_by_id(contract_id)

    async def create(self, data: ExpenseContractCreate):
        return await self.repo.create(data)

    async def update(self, contract_id: UUID, data: ExpenseContractUpdate):
        return await self.repo.update(contract_id, data)

    async def delete(self, contract_id: UUID):
        return await self.repo.delete(contract_id)


class ContractDistributionService:
    """Distribution management with SUM(%) ≤ 100 validation."""

    def __init__(self, session: AsyncSession):
        self.repo = ContractDistributionRepository(session)

    async def add_ls_income(self, data: LsIncomeContractCreate):
        return await self.repo.add_ls_income(data)

    async def remove_ls_income(self, ls_id: UUID, income_contract_id: UUID):
        return await self.repo.remove_ls_income(ls_id, income_contract_id)

    async def get_ls_income_links(self, ls_id: UUID):
        return await self.repo.get_ls_income_links(ls_id)

    async def add_income_expense(self, data: IncomeExpenseContractCreate):
        return await self.repo.add_income_expense(data)

    async def remove_income_expense(self, income_contract_id: UUID, expense_contract_id: UUID):
        return await self.repo.remove_income_expense(income_contract_id, expense_contract_id)

    async def get_income_expense_links(self, income_contract_id: UUID):
        return await self.repo.get_income_expense_links(income_contract_id)
