"""Pydantic v2 schemas for Project."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.projects.models import ProjectStatus


# ── Create / Update ──────────────────────────────────────────────
class ProjectCreate(BaseModel):
    code: str
    name: str
    customer: str | None = None
    contractor: str | None = None
    planned_start: date | None = None
    planned_end: date | None = None
    actual_start: date | None = None
    actual_end: date | None = None
    status: ProjectStatus = ProjectStatus.DESIGN


class ProjectUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    customer: str | None = None
    contractor: str | None = None
    planned_start: date | None = None
    planned_end: date | None = None
    actual_start: date | None = None
    actual_end: date | None = None
    status: ProjectStatus | None = None


# ── Read ─────────────────────────────────────────────────────────
class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    customer: str | None
    contractor: str | None
    planned_start: date | None
    planned_end: date | None
    actual_start: date | None
    actual_end: date | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime | None


class ProjectList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    customer: str | None
    status: ProjectStatus
