"""Pydantic v2 schemas for Estimate hierarchy (ССР → ОСР → ЛСР → ЛС → EstimateItem)."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.estimates.models import ExpertiseStatus, LocalEstimateType


# ══════════════════════════════════════════════════════════════════
# ССР — SummaryEstimate
# ══════════════════════════════════════════════════════════════════
class SummaryEstimateCreate(BaseModel):
    project_id: UUID
    code: str
    name: str
    total_amount: Decimal = Decimal("0")
    expertise_status: ExpertiseStatus = ExpertiseStatus.NOT_SUBMITTED
    expertise_date: date | None = None


class SummaryEstimateUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    total_amount: Decimal | None = None
    expertise_status: ExpertiseStatus | None = None
    expertise_date: date | None = None


class SummaryEstimateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    code: str
    name: str
    total_amount: Decimal
    expertise_status: ExpertiseStatus
    expertise_date: date | None
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# ОСР — ObjectEstimate
# ══════════════════════════════════════════════════════════════════
class ObjectEstimateCreate(BaseModel):
    summary_estimate_id: UUID
    code: str
    name: str
    total_amount: Decimal = Decimal("0")
    expertise_status: ExpertiseStatus = ExpertiseStatus.NOT_SUBMITTED


class ObjectEstimateUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    total_amount: Decimal | None = None
    expertise_status: ExpertiseStatus | None = None


class ObjectEstimateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    summary_estimate_id: UUID
    code: str
    name: str
    total_amount: Decimal
    expertise_status: ExpertiseStatus
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# ЛСР — LocalEstimateBase
# ══════════════════════════════════════════════════════════════════
class LocalEstimateBaseCreate(BaseModel):
    object_estimate_id: UUID
    code: str
    name: str
    total_amount: Decimal = Decimal("0")
    price_index: Decimal
    expertise_status: ExpertiseStatus = ExpertiseStatus.NOT_SUBMITTED


class LocalEstimateBaseUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    total_amount: Decimal | None = None
    price_index: Decimal | None = None
    expertise_status: ExpertiseStatus | None = None


class LocalEstimateBaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    object_estimate_id: UUID
    code: str
    name: str
    total_amount: Decimal
    price_index: Decimal
    expertise_status: ExpertiseStatus
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# ЛС — LocalEstimate
# ══════════════════════════════════════════════════════════════════
class LocalEstimateCreate(BaseModel):
    lsr_id: UUID
    code: str
    name: str
    type: LocalEstimateType = LocalEstimateType.MAIN
    total_amount: Decimal = Decimal("0")
    price_index: Decimal | None = None


class LocalEstimateUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    type: LocalEstimateType | None = None
    total_amount: Decimal | None = None
    price_index: Decimal | None = None


class LocalEstimateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    lsr_id: UUID
    code: str
    name: str
    type: LocalEstimateType
    total_amount: Decimal
    price_index: Decimal | None
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# EstimateItem — Сметная статья
# ══════════════════════════════════════════════════════════════════
class EstimateItemCreate(BaseModel):
    ls_id: UUID
    code: str
    name: str
    unit: str
    volume_approved: Decimal = Decimal("0")
    amount_approved: Decimal = Decimal("0")


class EstimateItemUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    unit: str | None = None
    volume_approved: Decimal | None = None
    amount_approved: Decimal | None = None


class EstimateItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ls_id: UUID
    code: str
    name: str
    unit: str
    volume_approved: Decimal
    amount_approved: Decimal
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# Tree node — для GET /projects/{id}/tree
# ══════════════════════════════════════════════════════════════════
class EstimateTreeNode(BaseModel):
    """Unified node for the estimate hierarchy tree."""
    id: UUID
    code: str
    name: str
    level: str  # SSR | OSR | LSR | LS | ITEM
    total_amount: Decimal
    amount_fact: Decimal = Decimal("0")
    amount_remaining: Decimal = Decimal("0")
    percent_complete: Decimal = Decimal("0")
    children: list["EstimateTreeNode"] = []


# ══════════════════════════════════════════════════════════════════
# Budget summary — для GET /projects/{id}/budget-summary
# ══════════════════════════════════════════════════════════════════
class BudgetSummaryItem(BaseModel):
    id: UUID
    code: str
    name: str
    level: str
    amount_approved: Decimal
    amount_fact: Decimal
    amount_remaining: Decimal
    percent_complete: Decimal
