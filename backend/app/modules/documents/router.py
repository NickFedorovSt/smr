"""FastAPI router for Documents (unified file storage)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.documents.models import EntityType
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate, DocumentRead
from app.modules.documents.service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    entity_type: EntityType | None = None,
    entity_id: UUID | None = None,
    session: AsyncSession = Depends(get_session),
):
    return await DocumentService(session).get_all(entity_type=entity_type, entity_id=entity_id)


@router.get("/{doc_id}", response_model=DocumentRead)
async def get_document(doc_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await DocumentService(session).get_by_id(doc_id)
    if not item:
        raise HTTPException(404, "Документ не найден")
    return item


@router.post("", response_model=DocumentRead, status_code=201)
async def create_document(data: DocumentCreate, session: AsyncSession = Depends(get_session)):
    return await DocumentService(session).create(data)


@router.put("/{doc_id}", response_model=DocumentRead)
async def update_document(doc_id: UUID, data: DocumentUpdate, session: AsyncSession = Depends(get_session)):
    item = await DocumentService(session).update(doc_id, data)
    if not item:
        raise HTTPException(404, "Документ не найден")
    return item


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await DocumentService(session).delete(doc_id):
        raise HTTPException(404, "Документ не найден")
