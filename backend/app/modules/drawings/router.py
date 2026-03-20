"""FastAPI router for Drawings + Specifications."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.drawings.schemas import (
    DrawingCreate, DrawingUpdate, DrawingRead,
    SpecificationCreate, SpecificationUpdate, SpecificationRead,
    LsDrawingLink,
)
from app.modules.drawings.service import DrawingService, SpecificationService

router = APIRouter(prefix="/drawings", tags=["drawings"])


# ── Drawing CRUD ─────────────────────────────────────────────────

@router.get("", response_model=list[DrawingRead])
async def list_drawings(project_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await DrawingService(session).get_all(project_id=project_id)


@router.get("/{drawing_id}", response_model=DrawingRead)
async def get_drawing(drawing_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await DrawingService(session).get_by_id(drawing_id)
    if not item:
        raise HTTPException(404, "Чертёж не найден")
    return item


@router.post("", response_model=DrawingRead, status_code=201)
async def create_drawing(data: DrawingCreate, session: AsyncSession = Depends(get_session)):
    return await DrawingService(session).create(data)


@router.put("/{drawing_id}", response_model=DrawingRead)
async def update_drawing(drawing_id: UUID, data: DrawingUpdate, session: AsyncSession = Depends(get_session)):
    item = await DrawingService(session).update(drawing_id, data)
    if not item:
        raise HTTPException(404, "Чертёж не найден")
    return item


@router.delete("/{drawing_id}", status_code=204)
async def delete_drawing(drawing_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await DrawingService(session).delete(drawing_id):
        raise HTTPException(404, "Чертёж не найден")


# ── ЛС ↔ Drawing link ───────────────────────────────────────────

@router.post("/link-ls", status_code=201)
async def link_drawing_to_ls(data: LsDrawingLink, session: AsyncSession = Depends(get_session)):
    await DrawingService(session).link_to_ls(data.ls_id, data.drawing_id)
    return {"status": "ok"}


@router.delete("/link-ls", status_code=204)
async def unlink_drawing_from_ls(ls_id: UUID, drawing_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await DrawingService(session).unlink_from_ls(ls_id, drawing_id):
        raise HTTPException(404, "Связь не найдена")


# ── Specification CRUD ───────────────────────────────────────────

@router.get("/specifications", response_model=list[SpecificationRead])
async def list_specifications(drawing_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await SpecificationService(session).get_all(drawing_id=drawing_id)


@router.get("/specifications/{spec_id}", response_model=SpecificationRead)
async def get_specification(spec_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await SpecificationService(session).get_by_id(spec_id)
    if not item:
        raise HTTPException(404, "Спецификация не найдена")
    return item


@router.post("/specifications", response_model=SpecificationRead, status_code=201)
async def create_specification(data: SpecificationCreate, session: AsyncSession = Depends(get_session)):
    return await SpecificationService(session).create(data)


@router.put("/specifications/{spec_id}", response_model=SpecificationRead)
async def update_specification(spec_id: UUID, data: SpecificationUpdate, session: AsyncSession = Depends(get_session)):
    item = await SpecificationService(session).update(spec_id, data)
    if not item:
        raise HTTPException(404, "Спецификация не найдена")
    return item


@router.delete("/specifications/{spec_id}", status_code=204)
async def delete_specification(spec_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await SpecificationService(session).delete(spec_id):
        raise HTTPException(404, "Спецификация не найдена")
