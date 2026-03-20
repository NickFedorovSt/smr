"""Pydantic v2 schemas for As-Built documentation (АОСР/АООК, WorkJournal, JournalEntry)."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.asbuilt.models import AsBuiltType, AsBuiltStatus, JournalType


# ══════════════════════════════════════════════════════════════════
# AsBuiltDoc
# ══════════════════════════════════════════════════════════════════
class AsBuiltDocCreate(BaseModel):
    project_id: UUID
    type: AsBuiltType
    number: str
    name: str
    work_date: date
    sign_date: date
    foreman: str
    supervisor: str
    status: AsBuiltStatus = AsBuiltStatus.DRAFT
    drawing_ids: list[UUID] = []
    specification_links: list["AsBuiltSpecLink"] = []


class AsBuiltDocUpdate(BaseModel):
    number: str | None = None
    name: str | None = None
    work_date: date | None = None
    sign_date: date | None = None
    foreman: str | None = None
    supervisor: str | None = None
    status: AsBuiltStatus | None = None


class AsBuiltDocRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    type: AsBuiltType
    number: str
    name: str
    work_date: date
    sign_date: date
    foreman: str
    supervisor: str
    status: AsBuiltStatus
    created_at: datetime
    updated_at: datetime | None


class AsBuiltSpecLink(BaseModel):
    """Link AsBuiltDoc → Specification with closed volume."""
    specification_id: UUID
    volume_closed: Decimal


# ══════════════════════════════════════════════════════════════════
# WorkJournal
# ══════════════════════════════════════════════════════════════════
class WorkJournalCreate(BaseModel):
    project_id: UUID
    type: JournalType
    name: str
    started_date: date


class WorkJournalUpdate(BaseModel):
    name: str | None = None
    started_date: date | None = None


class WorkJournalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    type: JournalType
    name: str
    started_date: date
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# JournalEntry
# ══════════════════════════════════════════════════════════════════
class JournalEntryCreate(BaseModel):
    journal_id: UUID
    entry_date: date
    description: str
    responsible: str


class JournalEntryUpdate(BaseModel):
    entry_date: date | None = None
    description: str | None = None
    responsible: str | None = None


class JournalEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    journal_id: UUID
    entry_date: date
    description: str
    responsible: str
    created_at: datetime
    updated_at: datetime | None
