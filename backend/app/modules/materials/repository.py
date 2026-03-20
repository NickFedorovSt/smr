"""Repository for MaterialCertificate, M29Report, M29Line."""

from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.materials.models import MaterialCertificate, M29Report, M29Line
from app.modules.materials.schemas import (
    MaterialCertificateCreate, MaterialCertificateUpdate,
    M29ReportCreate, M29ReportUpdate,
    M29LineCreate, M29LineUpdate,
)


class MaterialCertificateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, specification_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[MaterialCertificate]:
        stmt = select(MaterialCertificate)
        if specification_id:
            stmt = stmt.where(MaterialCertificate.specification_id == specification_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, cert_id: UUID) -> MaterialCertificate | None:
        result = await self.session.execute(
            select(MaterialCertificate).where(MaterialCertificate.id == cert_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: MaterialCertificateCreate) -> MaterialCertificate:
        cert = MaterialCertificate(**data.model_dump())
        self.session.add(cert)
        await self.session.flush()
        return cert

    async def update(self, cert_id: UUID, data: MaterialCertificateUpdate) -> MaterialCertificate | None:
        cert = await self.get_by_id(cert_id)
        if not cert:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cert, field, value)
        await self.session.flush()
        return cert

    async def delete(self, cert_id: UUID) -> bool:
        result = await self.session.execute(
            delete(MaterialCertificate).where(MaterialCertificate.id == cert_id)
        )
        return result.rowcount > 0


class M29ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, project_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[M29Report]:
        stmt = select(M29Report)
        if project_id:
            stmt = stmt.where(M29Report.project_id == project_id)
        result = await self.session.execute(
            stmt.offset(skip).limit(limit).order_by(M29Report.period_year, M29Report.period_month)
        )
        return list(result.scalars().all())

    async def get_by_id(self, report_id: UUID) -> M29Report | None:
        result = await self.session.execute(select(M29Report).where(M29Report.id == report_id))
        return result.scalar_one_or_none()

    async def create(self, data: M29ReportCreate) -> M29Report:
        report = M29Report(**data.model_dump())
        self.session.add(report)
        await self.session.flush()
        return report

    async def update(self, report_id: UUID, data: M29ReportUpdate) -> M29Report | None:
        report = await self.get_by_id(report_id)
        if not report:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(report, field, value)
        await self.session.flush()
        return report

    async def delete(self, report_id: UUID) -> bool:
        result = await self.session.execute(delete(M29Report).where(M29Report.id == report_id))
        return result.rowcount > 0


class M29LineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, report_id: UUID | None = None, skip: int = 0, limit: int = 100) -> list[M29Line]:
        stmt = select(M29Line)
        if report_id:
            stmt = stmt.where(M29Line.report_id == report_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, line_id: UUID) -> M29Line | None:
        result = await self.session.execute(select(M29Line).where(M29Line.id == line_id))
        return result.scalar_one_or_none()

    async def create(self, data: M29LineCreate) -> M29Line:
        line = M29Line(**data.model_dump())
        self.session.add(line)
        await self.session.flush()
        return line

    async def update(self, line_id: UUID, data: M29LineUpdate) -> M29Line | None:
        line = await self.get_by_id(line_id)
        if not line:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(line, field, value)
        await self.session.flush()
        return line

    async def delete(self, line_id: UUID) -> bool:
        result = await self.session.execute(delete(M29Line).where(M29Line.id == line_id))
        return result.rowcount > 0
