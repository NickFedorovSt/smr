"""Service layer for AsBuiltDoc, WorkJournal, JournalEntry."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.asbuilt.repository import (
    AsBuiltDocRepository,
    WorkJournalRepository,
    JournalEntryRepository,
)
from app.modules.asbuilt.schemas import (
    AsBuiltDocCreate, AsBuiltDocUpdate,
    WorkJournalCreate, WorkJournalUpdate,
    JournalEntryCreate, JournalEntryUpdate,
)


class AsBuiltDocService:
    def __init__(self, session: AsyncSession):
        self.repo = AsBuiltDocRepository(session)

    async def get_all(self, project_id: UUID | None = None):
        return await self.repo.get_all(project_id=project_id)

    async def get_by_id(self, doc_id: UUID):
        return await self.repo.get_by_id(doc_id)

    async def create(self, data: AsBuiltDocCreate):
        return await self.repo.create(data)

    async def update(self, doc_id: UUID, data: AsBuiltDocUpdate):
        return await self.repo.update(doc_id, data)

    async def delete(self, doc_id: UUID):
        return await self.repo.delete(doc_id)


class WorkJournalService:
    def __init__(self, session: AsyncSession):
        self.repo = WorkJournalRepository(session)

    async def get_all(self, project_id: UUID | None = None):
        return await self.repo.get_all(project_id=project_id)

    async def get_by_id(self, journal_id: UUID):
        return await self.repo.get_by_id(journal_id)

    async def create(self, data: WorkJournalCreate):
        return await self.repo.create(data)

    async def update(self, journal_id: UUID, data: WorkJournalUpdate):
        return await self.repo.update(journal_id, data)

    async def delete(self, journal_id: UUID):
        return await self.repo.delete(journal_id)


class JournalEntryService:
    def __init__(self, session: AsyncSession):
        self.repo = JournalEntryRepository(session)

    async def get_all(self, journal_id: UUID | None = None):
        return await self.repo.get_all(journal_id=journal_id)

    async def get_by_id(self, entry_id: UUID):
        return await self.repo.get_by_id(entry_id)

    async def create(self, data: JournalEntryCreate):
        return await self.repo.create(data)

    async def update(self, entry_id: UUID, data: JournalEntryUpdate):
        return await self.repo.update(entry_id, data)

    async def delete(self, entry_id: UUID):
        return await self.repo.delete(entry_id)
