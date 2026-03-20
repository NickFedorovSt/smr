"""Pydantic v2 schemas for Inspection + InspectionLog."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.inspections.models import InspectionStatus, InspectionEntityType


# ══════════════════════════════════════════════════════════════════
# Inspection
# ══════════════════════════════════════════════════════════════════
class InspectionCreate(BaseModel):
    project_id: UUID
    number: str
    description: str
    norm_reference: str | None = None
    planned_fix_date: date
    actual_fix_date: date | None = None
    status: InspectionStatus = InspectionStatus.OPEN
    related_entity_type: InspectionEntityType | None = None
    related_entity_id: UUID | None = None


class InspectionUpdate(BaseModel):
    number: str | None = None
    description: str | None = None
    norm_reference: str | None = None
    planned_fix_date: date | None = None
    actual_fix_date: date | None = None
    status: InspectionStatus | None = None
    related_entity_type: InspectionEntityType | None = None
    related_entity_id: UUID | None = None


class InspectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    number: str
    description: str
    norm_reference: str | None
    planned_fix_date: date
    actual_fix_date: date | None
    status: InspectionStatus
    related_entity_type: InspectionEntityType | None
    related_entity_id: UUID | None
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# Status change (Раздел 6.6 — атомарная смена статуса + лог)
# ══════════════════════════════════════════════════════════════════
class InspectionChangeStatus(BaseModel):
    """POST /inspections/{id}/change-status payload."""
    new_status: InspectionStatus
    comment: str | None = None
    changed_by: str | None = None


# ══════════════════════════════════════════════════════════════════
# InspectionLog
# ══════════════════════════════════════════════════════════════════
class InspectionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    inspection_id: UUID
    changed_at: datetime
    old_status: InspectionStatus
    new_status: InspectionStatus
    comment: str | None
    changed_by: str | None
    created_at: datetime
    updated_at: datetime | None
