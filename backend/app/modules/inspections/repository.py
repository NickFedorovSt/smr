"""Repository for Inspection + InspectionLog — CRUD + atomic status change (Раздел 6.6)."""

from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inspections.models import Inspection, InspectionLog
from app.modules.inspections.schemas import (
    InspectionCreate, InspectionUpdate,
    InspectionChangeStatus,
)


class InspectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        project_id: UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Inspection]:
        stmt = select(Inspection)
        if project_id:
            stmt = stmt.where(Inspection.project_id == project_id)
        if status:
            stmt = stmt.where(Inspection.status == status)
        result = await self.session.execute(stmt.offset(skip).limit(limit).order_by(Inspection.planned_fix_date))
        return list(result.scalars().all())

    async def get_by_id(self, inspection_id: UUID) -> Inspection | None:
        result = await self.session.execute(
            select(Inspection).where(Inspection.id == inspection_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: InspectionCreate) -> Inspection:
        inspection = Inspection(**data.model_dump())
        self.session.add(inspection)
        await self.session.flush()
        return inspection

    async def update(self, inspection_id: UUID, data: InspectionUpdate) -> Inspection | None:
        inspection = await self.get_by_id(inspection_id)
        if not inspection:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(inspection, field, value)
        await self.session.flush()
        return inspection

    async def delete(self, inspection_id: UUID) -> bool:
        result = await self.session.execute(
            delete(Inspection).where(Inspection.id == inspection_id)
        )
        return result.rowcount > 0

    async def change_status(self, inspection_id: UUID, data: InspectionChangeStatus) -> Inspection | None:
        """Atomic status change + InspectionLog creation (Раздел 6.6).

        POST /inspections/{id}/change-status
        Atomically: update Inspection.status + create InspectionLog entry.
        """
        inspection = await self.get_by_id(inspection_id)
        if not inspection:
            return None

        old_status = inspection.status
        inspection.status = data.new_status

        log_entry = InspectionLog(
            inspection_id=inspection_id,
            old_status=old_status,
            new_status=data.new_status,
            comment=data.comment,
            changed_by=data.changed_by,
        )
        self.session.add(log_entry)
        await self.session.flush()
        return inspection

    async def get_logs(self, inspection_id: UUID) -> list[InspectionLog]:
        result = await self.session.execute(
            select(InspectionLog)
            .where(InspectionLog.inspection_id == inspection_id)
            .order_by(InspectionLog.changed_at.desc())
        )
        return list(result.scalars().all())
