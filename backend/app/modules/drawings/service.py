"""Service layer for Drawings + Specifications."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.drawings.repository import DrawingRepository, SpecificationRepository
from app.modules.drawings.schemas import (
    DrawingCreate, DrawingUpdate,
    SpecificationCreate, SpecificationUpdate,
)


class DrawingService:
    def __init__(self, session: AsyncSession):
        self.repo = DrawingRepository(session)

    async def get_all(self, project_id: UUID | None = None):
        return await self.repo.get_all(project_id=project_id)

    async def get_by_id(self, drawing_id: UUID):
        return await self.repo.get_by_id(drawing_id)

    async def create(self, data: DrawingCreate):
        return await self.repo.create(data)

    async def update(self, drawing_id: UUID, data: DrawingUpdate):
        return await self.repo.update(drawing_id, data)

    async def delete(self, drawing_id: UUID):
        return await self.repo.delete(drawing_id)

    async def link_to_ls(self, ls_id: UUID, drawing_id: UUID):
        return await self.repo.link_to_ls(ls_id, drawing_id)

    async def unlink_from_ls(self, ls_id: UUID, drawing_id: UUID):
        return await self.repo.unlink_from_ls(ls_id, drawing_id)


class SpecificationService:
    def __init__(self, session: AsyncSession):
        self.repo = SpecificationRepository(session)

    async def get_all(self, drawing_id: UUID | None = None):
        return await self.repo.get_all(drawing_id=drawing_id)

    async def get_by_id(self, spec_id: UUID):
        return await self.repo.get_by_id(spec_id)

    async def create(self, data: SpecificationCreate):
        return await self.repo.create(data)

    async def update(self, spec_id: UUID, data: SpecificationUpdate):
        return await self.repo.update(spec_id, data)

    async def delete(self, spec_id: UUID):
        return await self.repo.delete(spec_id)
