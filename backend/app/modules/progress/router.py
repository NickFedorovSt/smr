"""FastAPI router for Progress (monthly actual work — КС-2)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.progress.schemas import ProgressCreate, ProgressUpdate, ProgressRead
from app.modules.progress.service import ProgressService

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=list[ProgressRead])
async def list_progress(
    estimate_item_id: UUID | None = None,
    year: int | None = None,
    month: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    return await ProgressService(session).get_all(
        estimate_item_id=estimate_item_id, year=year, month=month
    )


@router.get("/{progress_id}", response_model=ProgressRead)
async def get_progress(progress_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await ProgressService(session).get_by_id(progress_id)
    if not item:
        raise HTTPException(404, "Запись факта не найдена")
    return item


@router.post("", response_model=ProgressRead, status_code=201)
async def create_progress(data: ProgressCreate, session: AsyncSession = Depends(get_session)):
    try:
        return await ProgressService(session).create(data)
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.put("/{progress_id}", response_model=ProgressRead)
async def update_progress(progress_id: UUID, data: ProgressUpdate, session: AsyncSession = Depends(get_session)):
    item = await ProgressService(session).update(progress_id, data)
    if not item:
        raise HTTPException(404, "Запись факта не найдена")
    return item


@router.delete("/{progress_id}", status_code=204)
async def delete_progress(progress_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await ProgressService(session).delete(progress_id):
        raise HTTPException(404, "Запись факта не найдена")
