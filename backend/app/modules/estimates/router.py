"""FastAPI router for Estimate hierarchy — CRUD for ССР, ОСР, ЛСР, ЛС, EstimateItem."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.estimates.schemas import (
    SummaryEstimateCreate, SummaryEstimateUpdate, SummaryEstimateRead,
    ObjectEstimateCreate, ObjectEstimateUpdate, ObjectEstimateRead,
    LocalEstimateBaseCreate, LocalEstimateBaseUpdate, LocalEstimateBaseRead,
    LocalEstimateCreate, LocalEstimateUpdate, LocalEstimateRead,
    EstimateItemCreate, EstimateItemUpdate, EstimateItemRead,
)
from app.modules.estimates.service import (
    SummaryEstimateService,
    ObjectEstimateService,
    LocalEstimateBaseService,
    LocalEstimateService,
    EstimateItemService,
)

router = APIRouter(prefix="/estimates", tags=["estimates"])


# ── ССР — Сводный сметный расчёт ────────────────────────────────

@router.get("/ssr", response_model=list[SummaryEstimateRead])
async def list_ssr(project_id: UUID, session: AsyncSession = Depends(get_session)):
    return await SummaryEstimateService(session).get_by_project(project_id)


@router.get("/ssr/{ssr_id}", response_model=SummaryEstimateRead)
async def get_ssr(ssr_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await SummaryEstimateService(session).get_by_id(ssr_id)
    if not item:
        raise HTTPException(404, "ССР не найден")
    return item


@router.post("/ssr", response_model=SummaryEstimateRead, status_code=201)
async def create_ssr(data: SummaryEstimateCreate, session: AsyncSession = Depends(get_session)):
    return await SummaryEstimateService(session).create(data)


@router.put("/ssr/{ssr_id}", response_model=SummaryEstimateRead)
async def update_ssr(ssr_id: UUID, data: SummaryEstimateUpdate, session: AsyncSession = Depends(get_session)):
    item = await SummaryEstimateService(session).update(ssr_id, data)
    if not item:
        raise HTTPException(404, "ССР не найден")
    return item


@router.delete("/ssr/{ssr_id}", status_code=204)
async def delete_ssr(ssr_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await SummaryEstimateService(session).delete(ssr_id):
        raise HTTPException(404, "ССР не найден")


# ── ОСР — Объектный сметный расчёт ──────────────────────────────

@router.get("/osr", response_model=list[ObjectEstimateRead])
async def list_osr(summary_estimate_id: UUID, session: AsyncSession = Depends(get_session)):
    return await ObjectEstimateService(session).get_by_summary(summary_estimate_id)


@router.get("/osr/{osr_id}", response_model=ObjectEstimateRead)
async def get_osr(osr_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await ObjectEstimateService(session).get_by_id(osr_id)
    if not item:
        raise HTTPException(404, "ОСР не найден")
    return item


@router.post("/osr", response_model=ObjectEstimateRead, status_code=201)
async def create_osr(data: ObjectEstimateCreate, session: AsyncSession = Depends(get_session)):
    return await ObjectEstimateService(session).create(data)


@router.put("/osr/{osr_id}", response_model=ObjectEstimateRead)
async def update_osr(osr_id: UUID, data: ObjectEstimateUpdate, session: AsyncSession = Depends(get_session)):
    item = await ObjectEstimateService(session).update(osr_id, data)
    if not item:
        raise HTTPException(404, "ОСР не найден")
    return item


@router.delete("/osr/{osr_id}", status_code=204)
async def delete_osr(osr_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await ObjectEstimateService(session).delete(osr_id):
        raise HTTPException(404, "ОСР не найден")


# ── ЛСР — Локальный сметный расчёт ──────────────────────────────

@router.get("/lsr", response_model=list[LocalEstimateBaseRead])
async def list_lsr(object_estimate_id: UUID, session: AsyncSession = Depends(get_session)):
    return await LocalEstimateBaseService(session).get_by_object(object_estimate_id)


@router.get("/lsr/{lsr_id}", response_model=LocalEstimateBaseRead)
async def get_lsr(lsr_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await LocalEstimateBaseService(session).get_by_id(lsr_id)
    if not item:
        raise HTTPException(404, "ЛСР не найден")
    return item


@router.post("/lsr", response_model=LocalEstimateBaseRead, status_code=201)
async def create_lsr(data: LocalEstimateBaseCreate, session: AsyncSession = Depends(get_session)):
    return await LocalEstimateBaseService(session).create(data)


@router.put("/lsr/{lsr_id}", response_model=LocalEstimateBaseRead)
async def update_lsr(lsr_id: UUID, data: LocalEstimateBaseUpdate, session: AsyncSession = Depends(get_session)):
    item = await LocalEstimateBaseService(session).update(lsr_id, data)
    if not item:
        raise HTTPException(404, "ЛСР не найден")
    return item


@router.delete("/lsr/{lsr_id}", status_code=204)
async def delete_lsr(lsr_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await LocalEstimateBaseService(session).delete(lsr_id):
        raise HTTPException(404, "ЛСР не найден")


# ── ЛС — Локальная смета ────────────────────────────────────────

@router.get("/ls", response_model=list[LocalEstimateRead])
async def list_ls(lsr_id: UUID, session: AsyncSession = Depends(get_session)):
    return await LocalEstimateService(session).get_by_lsr(lsr_id)


@router.get("/ls/{ls_id}", response_model=LocalEstimateRead)
async def get_ls(ls_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await LocalEstimateService(session).get_by_id(ls_id)
    if not item:
        raise HTTPException(404, "ЛС не найдена")
    return item


@router.post("/ls", response_model=LocalEstimateRead, status_code=201)
async def create_ls(data: LocalEstimateCreate, session: AsyncSession = Depends(get_session)):
    return await LocalEstimateService(session).create(data)


@router.put("/ls/{ls_id}", response_model=LocalEstimateRead)
async def update_ls(ls_id: UUID, data: LocalEstimateUpdate, session: AsyncSession = Depends(get_session)):
    item = await LocalEstimateService(session).update(ls_id, data)
    if not item:
        raise HTTPException(404, "ЛС не найдена")
    return item


@router.delete("/ls/{ls_id}", status_code=204)
async def delete_ls(ls_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await LocalEstimateService(session).delete(ls_id):
        raise HTTPException(404, "ЛС не найдена")


# ── EstimateItem — Сметная статья ────────────────────────────────

@router.get("/items", response_model=list[EstimateItemRead])
async def list_items(ls_id: UUID, session: AsyncSession = Depends(get_session)):
    return await EstimateItemService(session).get_by_ls(ls_id)


@router.get("/items/{item_id}", response_model=EstimateItemRead)
async def get_item(item_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await EstimateItemService(session).get_by_id(item_id)
    if not item:
        raise HTTPException(404, "Сметная статья не найдена")
    return item


@router.post("/items", response_model=EstimateItemRead, status_code=201)
async def create_item(data: EstimateItemCreate, session: AsyncSession = Depends(get_session)):
    return await EstimateItemService(session).create(data)


@router.put("/items/{item_id}", response_model=EstimateItemRead)
async def update_item(item_id: UUID, data: EstimateItemUpdate, session: AsyncSession = Depends(get_session)):
    item = await EstimateItemService(session).update(item_id, data)
    if not item:
        raise HTTPException(404, "Сметная статья не найдена")
    return item


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await EstimateItemService(session).delete(item_id):
        raise HTTPException(404, "Сметная статья не найдена")
