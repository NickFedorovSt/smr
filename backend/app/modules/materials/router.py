"""FastAPI router for MaterialCertificate, M29Report, M29Line."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.materials.schemas import (
    MaterialCertificateCreate, MaterialCertificateUpdate, MaterialCertificateRead,
    M29ReportCreate, M29ReportUpdate, M29ReportRead,
    M29LineCreate, M29LineUpdate, M29LineRead,
)
from app.modules.materials.service import (
    MaterialCertificateService,
    M29ReportService,
    M29LineService,
)

router = APIRouter(prefix="/materials", tags=["materials"])


# ── MaterialCertificate ──────────────────────────────────────────

@router.get("/certificates", response_model=list[MaterialCertificateRead])
async def list_certificates(specification_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await MaterialCertificateService(session).get_all(specification_id=specification_id)


@router.get("/certificates/{cert_id}", response_model=MaterialCertificateRead)
async def get_certificate(cert_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await MaterialCertificateService(session).get_by_id(cert_id)
    if not item:
        raise HTTPException(404, "Сертификат не найден")
    return item


@router.post("/certificates", response_model=MaterialCertificateRead, status_code=201)
async def create_certificate(data: MaterialCertificateCreate, session: AsyncSession = Depends(get_session)):
    return await MaterialCertificateService(session).create(data)


@router.put("/certificates/{cert_id}", response_model=MaterialCertificateRead)
async def update_certificate(cert_id: UUID, data: MaterialCertificateUpdate, session: AsyncSession = Depends(get_session)):
    item = await MaterialCertificateService(session).update(cert_id, data)
    if not item:
        raise HTTPException(404, "Сертификат не найден")
    return item


@router.delete("/certificates/{cert_id}", status_code=204)
async def delete_certificate(cert_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await MaterialCertificateService(session).delete(cert_id):
        raise HTTPException(404, "Сертификат не найден")


# ── M29Report ────────────────────────────────────────────────────

@router.get("/m29", response_model=list[M29ReportRead])
async def list_m29_reports(project_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await M29ReportService(session).get_all(project_id=project_id)


@router.get("/m29/{report_id}", response_model=M29ReportRead)
async def get_m29_report(report_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await M29ReportService(session).get_by_id(report_id)
    if not item:
        raise HTTPException(404, "Отчёт М-29 не найден")
    return item


@router.post("/m29", response_model=M29ReportRead, status_code=201)
async def create_m29_report(data: M29ReportCreate, session: AsyncSession = Depends(get_session)):
    return await M29ReportService(session).create(data)


@router.put("/m29/{report_id}", response_model=M29ReportRead)
async def update_m29_report(report_id: UUID, data: M29ReportUpdate, session: AsyncSession = Depends(get_session)):
    item = await M29ReportService(session).update(report_id, data)
    if not item:
        raise HTTPException(404, "Отчёт М-29 не найден")
    return item


@router.delete("/m29/{report_id}", status_code=204)
async def delete_m29_report(report_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await M29ReportService(session).delete(report_id):
        raise HTTPException(404, "Отчёт М-29 не найден")


# ── M29Line ──────────────────────────────────────────────────────

@router.get("/m29-lines", response_model=list[M29LineRead])
async def list_m29_lines(report_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    return await M29LineService(session).get_all(report_id=report_id)


@router.get("/m29-lines/{line_id}", response_model=M29LineRead)
async def get_m29_line(line_id: UUID, session: AsyncSession = Depends(get_session)):
    item = await M29LineService(session).get_by_id(line_id)
    if not item:
        raise HTTPException(404, "Строка М-29 не найдена")
    return item


@router.post("/m29-lines", response_model=M29LineRead, status_code=201)
async def create_m29_line(data: M29LineCreate, session: AsyncSession = Depends(get_session)):
    return await M29LineService(session).create(data)


@router.put("/m29-lines/{line_id}", response_model=M29LineRead)
async def update_m29_line(line_id: UUID, data: M29LineUpdate, session: AsyncSession = Depends(get_session)):
    item = await M29LineService(session).update(line_id, data)
    if not item:
        raise HTTPException(404, "Строка М-29 не найдена")
    return item


@router.delete("/m29-lines/{line_id}", status_code=204)
async def delete_m29_line(line_id: UUID, session: AsyncSession = Depends(get_session)):
    if not await M29LineService(session).delete(line_id):
        raise HTTPException(404, "Строка М-29 не найдена")
