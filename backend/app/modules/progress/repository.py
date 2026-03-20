"""Repository for Progress (monthly actual work — КС-2)."""

from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.progress.models import Progress
from app.modules.progress.schemas import ProgressCreate, ProgressUpdate


class ProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        estimate_item_id: UUID | None = None,
        year: int | None = None,
        month: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:
        stmt = select(Progress)
        if estimate_item_id:
            stmt = stmt.where(Progress.estimate_item_id == estimate_item_id)
        if year:
            stmt = stmt.where(Progress.year == year)
        if month:
            stmt = stmt.where(Progress.month == month)
        result = await self.session.execute(
            stmt.offset(skip).limit(limit).order_by(Progress.year, Progress.month)
        )
        return list(result.scalars().all())

    async def get_by_id(self, progress_id: UUID) -> Progress | None:
        result = await self.session.execute(select(Progress).where(Progress.id == progress_id))
        return result.scalar_one_or_none()

    async def get_by_item_period(self, estimate_item_id: UUID, year: int, month: int) -> Progress | None:
        result = await self.session.execute(
            select(Progress).where(
                Progress.estimate_item_id == estimate_item_id,
                Progress.year == year,
                Progress.month == month,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, data: ProgressCreate) -> Progress:
        progress = Progress(**data.model_dump())
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def update(self, progress_id: UUID, data: ProgressUpdate) -> Progress | None:
        progress = await self.get_by_id(progress_id)
        if not progress:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(progress, field, value)
        await self.session.flush()
        return progress

    async def delete(self, progress_id: UUID) -> bool:
        result = await self.session.execute(delete(Progress).where(Progress.id == progress_id))
        return result.rowcount > 0
