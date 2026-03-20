"""Service layer for Estimate hierarchy — thin wrapper delegating to repositories."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.estimates.repository import (
    SummaryEstimateRepository,
    ObjectEstimateRepository,
    LocalEstimateBaseRepository,
    LocalEstimateRepository,
    EstimateItemRepository,
)
from app.modules.estimates.schemas import (
    SummaryEstimateCreate, SummaryEstimateUpdate,
    ObjectEstimateCreate, ObjectEstimateUpdate,
    LocalEstimateBaseCreate, LocalEstimateBaseUpdate,
    LocalEstimateCreate, LocalEstimateUpdate,
    EstimateItemCreate, EstimateItemUpdate,
)


class SummaryEstimateService:
    def __init__(self, session: AsyncSession):
        self.repo = SummaryEstimateRepository(session)

    async def get_by_project(self, project_id: UUID):
        return await self.repo.get_by_project(project_id)

    async def get_by_id(self, entity_id: UUID):
        return await self.repo.get_by_id(entity_id)

    async def create(self, data: SummaryEstimateCreate):
        return await self.repo.create(data)

    async def update(self, entity_id: UUID, data: SummaryEstimateUpdate):
        return await self.repo.update(entity_id, data)

    async def delete(self, entity_id: UUID):
        return await self.repo.delete(entity_id)


class ObjectEstimateService:
    def __init__(self, session: AsyncSession):
        self.repo = ObjectEstimateRepository(session)

    async def get_by_summary(self, summary_estimate_id: UUID):
        return await self.repo.get_by_summary(summary_estimate_id)

    async def get_by_id(self, entity_id: UUID):
        return await self.repo.get_by_id(entity_id)

    async def create(self, data: ObjectEstimateCreate):
        return await self.repo.create(data)

    async def update(self, entity_id: UUID, data: ObjectEstimateUpdate):
        return await self.repo.update(entity_id, data)

    async def delete(self, entity_id: UUID):
        return await self.repo.delete(entity_id)


class LocalEstimateBaseService:
    def __init__(self, session: AsyncSession):
        self.repo = LocalEstimateBaseRepository(session)

    async def get_by_object(self, object_estimate_id: UUID):
        return await self.repo.get_by_object(object_estimate_id)

    async def get_by_id(self, entity_id: UUID):
        return await self.repo.get_by_id(entity_id)

    async def create(self, data: LocalEstimateBaseCreate):
        return await self.repo.create(data)

    async def update(self, entity_id: UUID, data: LocalEstimateBaseUpdate):
        return await self.repo.update(entity_id, data)

    async def delete(self, entity_id: UUID):
        return await self.repo.delete(entity_id)


class LocalEstimateService:
    def __init__(self, session: AsyncSession):
        self.repo = LocalEstimateRepository(session)

    async def get_by_lsr(self, lsr_id: UUID):
        return await self.repo.get_by_lsr(lsr_id)

    async def get_by_id(self, entity_id: UUID):
        return await self.repo.get_by_id(entity_id)

    async def create(self, data: LocalEstimateCreate):
        return await self.repo.create(data)

    async def update(self, entity_id: UUID, data: LocalEstimateUpdate):
        return await self.repo.update(entity_id, data)

    async def delete(self, entity_id: UUID):
        return await self.repo.delete(entity_id)


class EstimateItemService:
    def __init__(self, session: AsyncSession):
        self.repo = EstimateItemRepository(session)

    async def get_by_ls(self, ls_id: UUID):
        return await self.repo.get_by_ls(ls_id)

    async def get_by_id(self, entity_id: UUID):
        return await self.repo.get_by_id(entity_id)

    async def create(self, data: EstimateItemCreate):
        return await self.repo.create(data)

    async def update(self, entity_id: UUID, data: EstimateItemUpdate):
        return await self.repo.update(entity_id, data)

    async def delete(self, entity_id: UUID):
        return await self.repo.delete(entity_id)
