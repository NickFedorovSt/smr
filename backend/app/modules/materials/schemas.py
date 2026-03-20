"""Pydantic v2 schemas for MaterialCertificate, M29Report, M29Line."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.materials.models import CertificateStatus, M29Status


# ══════════════════════════════════════════════════════════════════
# MaterialCertificate
# ══════════════════════════════════════════════════════════════════
class MaterialCertificateCreate(BaseModel):
    specification_id: UUID
    name: str
    document_number: str
    standard: str | None = None
    issue_date: date
    expiry_date: date | None = None
    status: CertificateStatus = CertificateStatus.PENDING
    rejection_reason: str | None = None


class MaterialCertificateUpdate(BaseModel):
    name: str | None = None
    document_number: str | None = None
    standard: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    status: CertificateStatus | None = None
    rejection_reason: str | None = None


class MaterialCertificateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    specification_id: UUID
    name: str
    document_number: str
    standard: str | None
    issue_date: date
    expiry_date: date | None
    status: CertificateStatus
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# M29Report
# ══════════════════════════════════════════════════════════════════
class M29ReportCreate(BaseModel):
    project_id: UUID
    period_month: int
    period_year: int
    foreman_name: str
    status: M29Status = M29Status.DRAFT

    @field_validator("period_month")
    @classmethod
    def validate_month(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise ValueError("Месяц должен быть от 1 до 12")
        return v


class M29ReportUpdate(BaseModel):
    foreman_name: str | None = None
    status: M29Status | None = None


class M29ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    period_month: int
    period_year: int
    foreman_name: str
    status: M29Status
    created_at: datetime
    updated_at: datetime | None


# ══════════════════════════════════════════════════════════════════
# M29Line
# ══════════════════════════════════════════════════════════════════
class M29LineCreate(BaseModel):
    report_id: UUID
    specification_id: UUID
    unit: str
    norm_consumption: Decimal = Decimal("0")
    actual_consumption: Decimal = Decimal("0")


class M29LineUpdate(BaseModel):
    norm_consumption: Decimal | None = None
    actual_consumption: Decimal | None = None


class M29LineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    report_id: UUID
    specification_id: UUID
    unit: str
    norm_consumption: Decimal
    actual_consumption: Decimal
    deviation: Decimal  # GENERATED COLUMN — read-only
    created_at: datetime
    updated_at: datetime | None
