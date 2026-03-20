"""Pydantic v2 schemas for Progress (monthly actual work — КС-2)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class ProgressCreate(BaseModel):
    estimate_item_id: UUID
    year: int
    month: int
    volume_fact: Decimal = Decimal("0")
    amount_fact: Decimal = Decimal("0")
    ks2_number: str | None = None

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise ValueError("Месяц должен быть от 1 до 12")
        return v


class ProgressUpdate(BaseModel):
    volume_fact: Decimal | None = None
    amount_fact: Decimal | None = None
    ks2_number: str | None = None


class ProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    estimate_item_id: UUID
    year: int
    month: int
    volume_fact: Decimal
    amount_fact: Decimal
    ks2_number: str | None
    created_at: datetime
    updated_at: datetime | None
