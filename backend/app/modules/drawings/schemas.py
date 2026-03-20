"""Pydantic v2 schemas for Drawing + Specification."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.drawings.models import DrawingStatus


# ── Drawing ──────────────────────────────────────────────────────
class DrawingCreate(BaseModel):
    project_id: UUID
    mark: str
    sheet_number: str
    revision: str = "0"
    name: str
    status: DrawingStatus = DrawingStatus.DRAFT
    issued_date: date | None = None


class DrawingUpdate(BaseModel):
    mark: str | None = None
    sheet_number: str | None = None
    revision: str | None = None
    name: str | None = None
    status: DrawingStatus | None = None
    issued_date: date | None = None


class DrawingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    mark: str
    sheet_number: str
    revision: str
    name: str
    status: DrawingStatus
    issued_date: date | None
    created_at: datetime
    updated_at: datetime | None


# ── Specification ────────────────────────────────────────────────
class SpecificationCreate(BaseModel):
    drawing_id: UUID
    position: str
    name: str
    mark_standard: str | None = None
    unit: str
    volume_designed: Decimal = Decimal("0")


class SpecificationUpdate(BaseModel):
    position: str | None = None
    name: str | None = None
    mark_standard: str | None = None
    unit: str | None = None
    volume_designed: Decimal | None = None


class SpecificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    drawing_id: UUID
    position: str
    name: str
    mark_standard: str | None
    unit: str
    volume_designed: Decimal
    created_at: datetime
    updated_at: datetime | None


# ── Link ЛС ↔ Drawing ───────────────────────────────────────────
class LsDrawingLink(BaseModel):
    ls_id: UUID
    drawing_id: UUID
