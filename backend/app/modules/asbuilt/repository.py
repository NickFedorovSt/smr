"""Repository for AsBuiltDoc, WorkJournal, JournalEntry — CRUD + link management."""

from uuid import UUID

from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.asbuilt.models import (
    AsBuiltDoc,
    WorkJournal,
    JournalEntry,
    asbuilt_drawing,
    asbuilt_specification,
)
from app.modules.asbuilt.schemas import (
    AsBuiltDocCreate, AsBuiltDocUpdate,
    WorkJournalCreate, WorkJournalUpdate,
    JournalEntryCreate, JournalEntryUpdate,
)


class AsBuiltDocRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, project_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[AsBuiltDoc]:
        stmt = select(AsBuiltDoc)
        if project_id:
            stmt = stmt.where(AsBuiltDoc.project_id == project_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit).order_by(AsBuiltDoc.number))
        return list(result.scalars().all())

    async def get_by_id(self, doc_id: UUID) -> AsBuiltDoc | None:
        result = await self.session.execute(select(AsBuiltDoc).where(AsBuiltDoc.id == doc_id))
        return result.scalar_one_or_none()

    async def create(self, data: AsBuiltDocCreate) -> AsBuiltDoc:
        create_data = data.model_dump(exclude={"drawing_ids", "specification_links"})
        doc = AsBuiltDoc(**create_data)
        self.session.add(doc)
        await self.session.flush()

        # Link drawings
        for drawing_id in data.drawing_ids:
            await self.session.execute(
                insert(asbuilt_drawing).values(asbuilt_id=doc.id, drawing_id=drawing_id)
            )

        # Link specifications with volume_closed
        for link in data.specification_links:
            await self.session.execute(
                insert(asbuilt_specification).values(
                    asbuilt_id=doc.id,
                    specification_id=link.specification_id,
                    volume_closed=link.volume_closed,
                )
            )

        await self.session.flush()
        return doc

    async def update(self, doc_id: UUID, data: AsBuiltDocUpdate) -> AsBuiltDoc | None:
        doc = await self.get_by_id(doc_id)
        if not doc:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(doc, field, value)
        await self.session.flush()
        return doc

    async def delete(self, doc_id: UUID) -> bool:
        result = await self.session.execute(delete(AsBuiltDoc).where(AsBuiltDoc.id == doc_id))
        return result.rowcount > 0


class WorkJournalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, project_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[WorkJournal]:
        stmt = select(WorkJournal)
        if project_id:
            stmt = stmt.where(WorkJournal.project_id == project_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, journal_id: UUID) -> WorkJournal | None:
        result = await self.session.execute(select(WorkJournal).where(WorkJournal.id == journal_id))
        return result.scalar_one_or_none()

    async def create(self, data: WorkJournalCreate) -> WorkJournal:
        journal = WorkJournal(**data.model_dump())
        self.session.add(journal)
        await self.session.flush()
        return journal

    async def update(self, journal_id: UUID, data: WorkJournalUpdate) -> WorkJournal | None:
        journal = await self.get_by_id(journal_id)
        if not journal:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(journal, field, value)
        await self.session.flush()
        return journal

    async def delete(self, journal_id: UUID) -> bool:
        result = await self.session.execute(delete(WorkJournal).where(WorkJournal.id == journal_id))
        return result.rowcount > 0


class JournalEntryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, journal_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[JournalEntry]:
        stmt = select(JournalEntry)
        if journal_id:
            stmt = stmt.where(JournalEntry.journal_id == journal_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit).order_by(JournalEntry.entry_date))
        return list(result.scalars().all())

    async def get_by_id(self, entry_id: UUID) -> JournalEntry | None:
        result = await self.session.execute(select(JournalEntry).where(JournalEntry.id == entry_id))
        return result.scalar_one_or_none()

    async def create(self, data: JournalEntryCreate) -> JournalEntry:
        entry = JournalEntry(**data.model_dump())
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def update(self, entry_id: UUID, data: JournalEntryUpdate) -> JournalEntry | None:
        entry = await self.get_by_id(entry_id)
        if not entry:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(entry, field, value)
        await self.session.flush()
        return entry

    async def delete(self, entry_id: UUID) -> bool:
        result = await self.session.execute(delete(JournalEntry).where(JournalEntry.id == entry_id))
        return result.rowcount > 0
