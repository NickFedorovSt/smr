"""Service layer for MaterialCertificate, M29Report, M29Line."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.materials.repository import (
    MaterialCertificateRepository,
    M29ReportRepository,
    M29LineRepository,
)
from app.modules.materials.schemas import (
    MaterialCertificateCreate, MaterialCertificateUpdate,
    M29ReportCreate, M29ReportUpdate,
    M29LineCreate, M29LineUpdate,
)


class MaterialCertificateService:
    def __init__(self, session: AsyncSession):
        self.repo = MaterialCertificateRepository(session)

    async def get_all(self, specification_id: UUID | None = None):
        return await self.repo.get_all(specification_id=specification_id)

    async def get_by_id(self, cert_id: UUID):
        return await self.repo.get_by_id(cert_id)

    async def create(self, data: MaterialCertificateCreate):
        return await self.repo.create(data)

    async def update(self, cert_id: UUID, data: MaterialCertificateUpdate):
        return await self.repo.update(cert_id, data)

    async def delete(self, cert_id: UUID):
        return await self.repo.delete(cert_id)


class M29ReportService:
    def __init__(self, session: AsyncSession):
        self.repo = M29ReportRepository(session)

    async def get_all(self, project_id: UUID | None = None):
        return await self.repo.get_all(project_id=project_id)

    async def get_by_id(self, report_id: UUID):
        return await self.repo.get_by_id(report_id)

    async def create(self, data: M29ReportCreate):
        return await self.repo.create(data)

    async def update(self, report_id: UUID, data: M29ReportUpdate):
        return await self.repo.update(report_id, data)

    async def delete(self, report_id: UUID):
        return await self.repo.delete(report_id)


class M29LineService:
    def __init__(self, session: AsyncSession):
        self.repo = M29LineRepository(session)

    async def get_all(self, report_id: UUID | None = None):
        return await self.repo.get_all(report_id=report_id)

    async def get_by_id(self, line_id: UUID):
        return await self.repo.get_by_id(line_id)

    async def create(self, data: M29LineCreate):
        return await self.repo.create(data)

    async def update(self, line_id: UUID, data: M29LineUpdate):
        return await self.repo.update(line_id, data)

    async def delete(self, line_id: UUID):
        return await self.repo.delete(line_id)
