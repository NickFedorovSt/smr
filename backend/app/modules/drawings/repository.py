"""Repository for Drawing + Specification CRUD."""

from uuid import UUID

from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.drawings.models import Drawing, Specification, ls_drawing
from app.modules.drawings.schemas import (
    DrawingCreate, DrawingUpdate,
    SpecificationCreate, SpecificationUpdate,
)


class DrawingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, project_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[Drawing]:
        stmt = select(Drawing)
        if project_id:
            stmt = stmt.where(Drawing.project_id == project_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit).order_by(Drawing.mark, Drawing.sheet_number))
        return list(result.scalars().all())

    async def get_by_id(self, drawing_id: UUID) -> Drawing | None:
        result = await self.session.execute(select(Drawing).where(Drawing.id == drawing_id))
        return result.scalar_one_or_none()

    async def create(self, data: DrawingCreate) -> Drawing:
        drawing = Drawing(**data.model_dump())
        self.session.add(drawing)
        await self.session.flush()
        return drawing

    async def update(self, drawing_id: UUID, data: DrawingUpdate) -> Drawing | None:
        drawing = await self.get_by_id(drawing_id)
        if not drawing:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(drawing, field, value)
        await self.session.flush()
        return drawing

    async def delete(self, drawing_id: UUID) -> bool:
        result = await self.session.execute(delete(Drawing).where(Drawing.id == drawing_id))
        return result.rowcount > 0

    # ── ЛС ↔ Drawing links ──────────────────────────────────────
    async def link_to_ls(self, ls_id: UUID, drawing_id: UUID) -> None:
        await self.session.execute(
            insert(ls_drawing).values(ls_id=ls_id, drawing_id=drawing_id)
        )
        await self.session.flush()

    async def unlink_from_ls(self, ls_id: UUID, drawing_id: UUID) -> bool:
        result = await self.session.execute(
            delete(ls_drawing).where(
                ls_drawing.c.ls_id == ls_id,
                ls_drawing.c.drawing_id == drawing_id,
            )
        )
        return result.rowcount > 0


class SpecificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, drawing_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[Specification]:
        stmt = select(Specification)
        if drawing_id:
            stmt = stmt.where(Specification.drawing_id == drawing_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit).order_by(Specification.position))
        return list(result.scalars().all())

    async def get_by_id(self, spec_id: UUID) -> Specification | None:
        result = await self.session.execute(select(Specification).where(Specification.id == spec_id))
        return result.scalar_one_or_none()

    async def create(self, data: SpecificationCreate) -> Specification:
        spec = Specification(**data.model_dump())
        self.session.add(spec)
        await self.session.flush()
        return spec

    async def update(self, spec_id: UUID, data: SpecificationUpdate) -> Specification | None:
        spec = await self.get_by_id(spec_id)
        if not spec:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(spec, field, value)
        await self.session.flush()
        return spec

    async def delete(self, spec_id: UUID) -> bool:
        result = await self.session.execute(delete(Specification).where(Specification.id == spec_id))
        return result.rowcount > 0
