"""Document model — 4.5 ЕДИНОЕ ФАЙЛОВОЕ ХРАНИЛИЩЕ.

Polymorphic file storage linked to any entity via entity_type + entity_id.
"""

import enum
import uuid

from sqlalchemy import BigInteger, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EntityType(str, enum.Enum):
    DRAWING = "DRAWING"
    ASBUILT = "ASBUILT"
    CERTIFICATE = "CERTIFICATE"
    M29 = "M29"
    INSPECTION = "INSPECTION"
    REPORT = "REPORT"
    OTHER = "OTHER"


class Document(Base):
    __tablename__ = "documents"

    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, name="entity_type"),
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)  # MinIO bucket/key
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str | None] = mapped_column(String(32))  # md5
    uploaded_by: Mapped[str | None] = mapped_column(String(200))
