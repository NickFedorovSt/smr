"""FastAPI router for AsBuiltDoc, WorkJournal, JournalEntry."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.asbuilt.schemas import (
    AsBuiltDocCreate, AsBuiltDocUpdate, AsBuiltDocRead,
    WorkJournalCreate, WorkJournalUpdate, WorkJournalRead,
    JournalEntryCreate, JournalEntryUpdate, JournalEntryRead,
)
from app.modules.asbuilt.service import (
    AsBuiltDocService,
    WorkJournalService,
    JournalEntryService,
)

router = APIRouter(prefix="/asbuilt", tags=["asbuilt"])


# ── AsBuiltDoc (АОСР/АООК) ──────────────────────────────────────

@router.get("/docs", response_model=list[AsBuiltDocRead])
async def list_asbuilt_docs(project_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await AsBuiltDocService(session).get_all(project_id=project_id)


@router.get("/docs/{doc_id}", response_model=AsBuiltDocRead)
async def get_asbuilt_doc(doc_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await AsBuiltDocService(session).get_by_id(doc_id)
    if not item:
        raise HTTPException(404, "Акт ИД не найден")
    return item


@router.post("/docs", response_model=AsBuiltDocRead, status_code=201)
async def create_asbuilt_doc(data: AsBuiltDocCreate, session: AsyncSession = Depends(get_session)):
    return await AsBuiltDocService(session).create(data)


@router.put("/docs/{doc_id}", response_model=AsBuiltDocRead)
async def update_asbuilt_doc(doc_id: UUID, data: AsBuiltDocUpdate, session: AsyncSession = Depends(get_session)):
    item = await AsBuiltDocService(session).update(doc_id, data)
    if not item:
        raise HTTPException(404, "Акт ИД не найден")
    return item


@router.delete("/docs/{doc_id}", status_code=204)
async def delete_asbuilt_doc(doc_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await AsBuiltDocService(session).delete(doc_id):
        raise HTTPException(404, "Акт ИД не найден")


# ── WorkJournal (ОЖР) ───────────────────────────────────────────

@router.get("/journals", response_model=list[WorkJournalRead])
async def list_journals(project_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await WorkJournalService(session).get_all(project_id=project_id)


@router.get("/journals/{journal_id}", response_model=WorkJournalRead)
async def get_journal(journal_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await WorkJournalService(session).get_by_id(journal_id)
    if not item:
        raise HTTPException(404, "Журнал не найден")
    return item


@router.post("/journals", response_model=WorkJournalRead, status_code=201)
async def create_journal(data: WorkJournalCreate, session: AsyncSession = Depends(get_session)):
    return await WorkJournalService(session).create(data)


@router.put("/journals/{journal_id}", response_model=WorkJournalRead)
async def update_journal(journal_id: UUID, data: WorkJournalUpdate, session: AsyncSession = Depends(get_session)):
    item = await WorkJournalService(session).update(journal_id, data)
    if not item:
        raise HTTPException(404, "Журнал не найден")
    return item


@router.delete("/journals/{journal_id}", status_code=204)
async def delete_journal(journal_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await WorkJournalService(session).delete(journal_id):
        raise HTTPException(404, "Журнал не найден")


# ── JournalEntry ─────────────────────────────────────────────────

@router.get("/entries", response_model=list[JournalEntryRead])
async def list_entries(journal_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await JournalEntryService(session).get_all(journal_id=journal_id)


@router.get("/entries/{entry_id}", response_model=JournalEntryRead)
async def get_entry(entry_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await JournalEntryService(session).get_by_id(entry_id)
    if not item:
        raise HTTPException(404, "Запись журнала не найдена")
    return item


@router.post("/entries", response_model=JournalEntryRead, status_code=201)
async def create_entry(data: JournalEntryCreate, session: AsyncSession = Depends(get_session)):
    return await JournalEntryService(session).create(data)


@router.put("/entries/{entry_id}", response_model=JournalEntryRead)
async def update_entry(entry_id: UUID, data: JournalEntryUpdate, session: AsyncSession = Depends(get_session)):
    item = await JournalEntryService(session).update(entry_id, data)
    if not item:
        raise HTTPException(404, "Запись журнала не найдена")
    return item


@router.delete("/entries/{entry_id}", status_code=204)
async def delete_entry(entry_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await JournalEntryService(session).delete(entry_id):
        raise HTTPException(404, "Запись журнала не найдена")
