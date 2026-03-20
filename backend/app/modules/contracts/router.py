"""FastAPI router for Contracts — CRUD + distribution links (Раздел 6.5)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.contracts.schemas import (
    IncomeContractCreate, IncomeContractUpdate, IncomeContractRead,
    ExpenseContractCreate, ExpenseContractUpdate, ExpenseContractRead,
    LsIncomeContractCreate, LsIncomeContractRead,
    IncomeExpenseContractCreate, IncomeExpenseContractRead,
)
from app.modules.contracts.service import (
    IncomeContractService,
    ExpenseContractService,
    ContractDistributionService,
)

router = APIRouter(prefix="/contracts", tags=["contracts"])


# ── IncomeContract ───────────────────────────────────────────────

@router.get("/income", response_model=list[IncomeContractRead])
async def list_income(project_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await IncomeContractService(session).get_all(project_id=project_id)


@router.get("/income/{contract_id}", response_model=IncomeContractRead)
async def get_income(contract_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await IncomeContractService(session).get_by_id(contract_id)
    if not item:
        raise HTTPException(404, "Доходный договор не найден")
    return item


@router.post("/income", response_model=IncomeContractRead, status_code=201)
async def create_income(data: IncomeContractCreate, session: AsyncSession = Depends(get_session)):
    return await IncomeContractService(session).create(data)


@router.put("/income/{contract_id}", response_model=IncomeContractRead)
async def update_income(contract_id: UUID, data: IncomeContractUpdate, session: AsyncSession = Depends(get_session)):
    item = await IncomeContractService(session).update(contract_id, data)
    if not item:
        raise HTTPException(404, "Доходный договор не найден")
    return item


@router.delete("/income/{contract_id}", status_code=204)
async def delete_income(contract_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await IncomeContractService(session).delete(contract_id):
        raise HTTPException(404, "Доходный договор не найден")


# ── ExpenseContract ──────────────────────────────────────────────

@router.get("/expense", response_model=list[ExpenseContractRead])
async def list_expense(project_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await ExpenseContractService(session).get_all(project_id=project_id)


@router.get("/expense/{contract_id}", response_model=ExpenseContractRead)
async def get_expense(contract_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await ExpenseContractService(session).get_by_id(contract_id)
    if not item:
        raise HTTPException(404, "Расходный договор не найден")
    return item


@router.post("/expense", response_model=ExpenseContractRead, status_code=201)
async def create_expense(data: ExpenseContractCreate, session: AsyncSession = Depends(get_session)):
    return await ExpenseContractService(session).create(data)


@router.put("/expense/{contract_id}", response_model=ExpenseContractRead)
async def update_expense(contract_id: UUID, data: ExpenseContractUpdate, session: AsyncSession = Depends(get_session)):
    item = await ExpenseContractService(session).update(contract_id, data)
    if not item:
        raise HTTPException(404, "Расходный договор не найден")
    return item


@router.delete("/expense/{contract_id}", status_code=204)
async def delete_expense(contract_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await ExpenseContractService(session).delete(contract_id):
        raise HTTPException(404, "Расходный договор не найден")


# ── Distribution: ЛС ↔ IncomeContract (Раздел 6.5) ──────────────

@router.post("/ls-income", status_code=201)
async def add_ls_income(data: LsIncomeContractCreate, session: AsyncSession = Depends(get_session)):
    """POST /contracts/ls-income — привязка ЛС к доходному договору.

    Валидация: SUM(percentage) по ls_id ≤ 100, иначе HTTP 422.
    """
    try:
        await ContractDistributionService(session).add_ls_income(data)
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.delete("/ls-income", status_code=204)
async def remove_ls_income(ls_id: UUID, income_contract_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await ContractDistributionService(session).remove_ls_income(ls_id, income_contract_id):
        raise HTTPException(404, "Связь не найдена")


@router.get("/ls-income", response_model=list[LsIncomeContractRead])
async def get_ls_income_links(ls_id: UUID, session: AsyncSession = Depends(get_session)):
    return await ContractDistributionService(session).get_ls_income_links(ls_id)


# ── Distribution: IncomeContract ↔ ExpenseContract ───────────────

@router.post("/income-expense", status_code=201)
async def add_income_expense(data: IncomeExpenseContractCreate, session: AsyncSession = Depends(get_session)):
    try:
        await ContractDistributionService(session).add_income_expense(data)
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.delete("/income-expense", status_code=204)
async def remove_income_expense(
    income_contract_id: UUID, expense_contract_id: UUID, session: AsyncSession = Depends(get_session)
):
    if not await ContractDistributionService(session).remove_income_expense(income_contract_id, expense_contract_id):
        raise HTTPException(404, "Связь не найдена")


@router.get("/income-expense", response_model=list[IncomeExpenseContractRead])
async def get_income_expense_links(income_contract_id: UUID, session: AsyncSession = Depends(get_session)):
    return await ContractDistributionService(session).get_income_expense_links(income_contract_id)
