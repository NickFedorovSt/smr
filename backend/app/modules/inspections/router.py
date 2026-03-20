"""FastAPI router for Inspections — CRUD + change-status (Раздел 6.6)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.inspections.schemas import (
    InspectionCreate, InspectionUpdate, InspectionRead,
    InspectionChangeStatus,
    InspectionLogRead,
)
from app.modules.inspections.service import InspectionService

router = APIRouter(prefix="/inspections", tags=["inspections"])


@router.get("", response_model=list[InspectionRead])
async def list_inspections(
    project_id: UUID | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    return await InspectionService(session).get_all(project_id=project_id, status=status)


@router.get("/{inspection_id}", response_model=InspectionRead)
async def get_inspection(inspection_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await InspectionService(session).get_by_id(inspection_id)
    if not item:
        raise HTTPException(404, "Предписание не найдено")
    return item


@router.post("", response_model=InspectionRead, status_code=201)
async def create_inspection(data: InspectionCreate, session: AsyncSession = Depends(get_session)):
    return await InspectionService(session).create(data)


@router.put("/{inspection_id}", response_model=InspectionRead)
async def update_inspection(
    inspection_id: UUID, data: InspectionUpdate, session: AsyncSession = Depends(get_session)
):
    item = await InspectionService(session).update(inspection_id, data)
    if not item:
        raise HTTPException(404, "Предписание не найдено")
    return item


@router.delete("/{inspection_id}", status_code=204)
async def delete_inspection(inspection_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await InspectionService(session).delete(inspection_id):
        raise HTTPException(404, "Предписание не найдено")


# ── Change status (Раздел 6.6) ──────────────────────────────────

@router.post("/{inspection_id}/change-status", response_model=InspectionRead)
async def change_inspection_status(
    inspection_id: UUID,
    data: InspectionChangeStatus,
    session: AsyncSession = Depends(get_session),
):
    """POST /inspections/{id}/change-status — атомарно: обновить статус + создать InspectionLog."""
    item = await InspectionService(session).change_status(inspection_id, data)
    if not item:
        raise HTTPException(404, "Предписание не найдено")
    return item


@router.get("/{inspection_id}/logs", response_model=list[InspectionLogRead])
async def get_inspection_logs(inspection_id: UUID, session: AsyncSession = Depends(get_session)):
    return await InspectionService(session).get_logs(inspection_id)
