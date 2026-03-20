"""Service layer for Progress (monthly actual work — КС-2)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.progress.repository import ProgressRepository
from app.modules.progress.schemas import ProgressCreate, ProgressUpdate


class ProgressService:
    def __init__(self, session: AsyncSession):
        self.repo = ProgressRepository(session)

    async def get_all(self, estimate_item_id: UUID | None = None, year: int | None = None, month: int | None = None):
        return await self.repo.get_all(estimate_item_id=estimate_item_id, year=year, month=month)

    async def get_by_id(self, progress_id: UUID):
        return await self.repo.get_by_id(progress_id)

    async def create(self, data: ProgressCreate):
        # Check for duplicate period
        existing = await self.repo.get_by_item_period(data.estimate_item_id, data.year, data.month)
        if existing:
            raise ValueError(
                f"Запись за {data.month:02d}.{data.year} для данной статьи уже существует"
            )
        return await self.repo.create(data)

    async def update(self, progress_id: UUID, data: ProgressUpdate):
        return await self.repo.update(progress_id, data)

    async def delete(self, progress_id: UUID):
        return await self.repo.delete(progress_id)
