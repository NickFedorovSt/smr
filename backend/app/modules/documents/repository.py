"""Repository for Document CRUD — unified file storage linked to any entity."""

from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import Document, EntityType
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        entity_type: EntityType | None = None,
        entity_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        stmt = select(Document)
        if entity_type:
            stmt = stmt.where(Document.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(Document.entity_id == entity_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit).order_by(Document.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, doc_id: UUID) -> Document | None:
        result = await self.session.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def get_by_entity(self, entity_type: EntityType, entity_id: UUID) -> list[Document]:
        return await self.get_all(entity_type=entity_type, entity_id=entity_id)

    async def create(self, data: DocumentCreate) -> Document:
        doc = Document(**data.model_dump())
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def update(self, doc_id: UUID, data: DocumentUpdate) -> Document | None:
        doc = await self.get_by_id(doc_id)
        if not doc:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(doc, field, value)
        await self.session.flush()
        return doc

    async def delete(self, doc_id: UUID) -> bool:
        result = await self.session.execute(delete(Document).where(Document.id == doc_id))
        return result.rowcount > 0
