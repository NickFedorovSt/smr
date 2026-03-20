"""Service layer for Documents (unified file storage)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import EntityType
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate


class DocumentService:
    def __init__(self, session: AsyncSession):
        self.repo = DocumentRepository(session)

    async def get_all(self, entity_type: EntityType | None = None, entity_id: UUID | None = None):
        return await self.repo.get_all(entity_type=entity_type, entity_id=entity_id)

    async def get_by_id(self, doc_id: UUID):
        return await self.repo.get_by_id(doc_id)

    async def get_by_entity(self, entity_type: EntityType, entity_id: UUID):
        return await self.repo.get_by_entity(entity_type, entity_id)

    async def create(self, data: DocumentCreate):
        return await self.repo.create(data)

    async def update(self, doc_id: UUID, data: DocumentUpdate):
        return await self.repo.update(doc_id, data)

    async def delete(self, doc_id: UUID):
        return await self.repo.delete(doc_id)
