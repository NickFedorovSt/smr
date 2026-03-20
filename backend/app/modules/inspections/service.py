"""Service layer for Inspections — CRUD + atomic status change (Раздел 6.6)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inspections.repository import InspectionRepository
from app.modules.inspections.schemas import (
    InspectionCreate, InspectionUpdate,
    InspectionChangeStatus,
)


class InspectionService:
    def __init__(self, session: AsyncSession):
        self.repo = InspectionRepository(session)

    async def get_all(self, project_id: UUID | None = None, status: str | None = None):
        return await self.repo.get_all(project_id=project_id, status=status)

    async def get_by_id(self, inspection_id: UUID):
        return await self.repo.get_by_id(inspection_id)

    async def create(self, data: InspectionCreate):
        return await self.repo.create(data)

    async def update(self, inspection_id: UUID, data: InspectionUpdate):
        return await self.repo.update(inspection_id, data)

    async def delete(self, inspection_id: UUID):
        return await self.repo.delete(inspection_id)

    async def change_status(self, inspection_id: UUID, data: InspectionChangeStatus):
        """Раздел 6.6 — атомарная смена статуса + запись в InspectionLog."""
        return await self.repo.change_status(inspection_id, data)

    async def get_logs(self, inspection_id: UUID):
        return await self.repo.get_logs(inspection_id)
