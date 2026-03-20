"""Pydantic v2 schemas for Document (unified file storage)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.documents.models import EntityType


class DocumentCreate(BaseModel):
    entity_type: EntityType
    entity_id: UUID
    file_name: str
    file_path: str
    mime_type: str
    file_size: int
    version: int = 1
    checksum: str | None = None
    uploaded_by: str | None = None


class DocumentUpdate(BaseModel):
    file_name: str | None = None
    file_path: str | None = None
    version: int | None = None
    checksum: str | None = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    entity_type: EntityType
    entity_id: UUID
    file_name: str
    file_path: str
    mime_type: str
    file_size: int
    version: int
    checksum: str | None
    uploaded_by: str | None
    created_at: datetime
    updated_at: datetime | None
