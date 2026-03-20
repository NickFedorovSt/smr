"""Reports router — GET /reports/generate, GET /reports/list, DELETE /reports/{id}.

Раздел 6.7 — генерация отчётов с кэшированием.
Flow:
  1. GET /reports/generate → ReportService.generate() → FileResponse / StreamingResponse
  2. GET /reports/list → ReportService.list_reports()
  3. DELETE /reports/{id} → ReportService.delete_report()
  BackgroundTask: cleanup temp if needed.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.reports.schemas import ReportType
from app.modules.reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def _service(session: AsyncSession = Depends(get_session)) -> ReportService:
    return ReportService(session)


def _cleanup_temp(path: str) -> None:
    """Background task: remove temp file after response is sent."""
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass


@router.get("/generate")
async def generate_report(
    background_tasks: BackgroundTasks,
    type: ReportType = Query(..., description="Тип отчёта"),
    project_id: UUID | None = None,
    year: int | None = None,
    month: int | None = None,
    month_from: int | None = None,
    month_to: int | None = None,
    contract_type: str | None = None,
    income_contract_id: UUID | None = None,
    ls_id: UUID | None = None,
    journal_id: UUID | None = None,
    report_id: UUID | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    level: str | None = None,
    service: ReportService = Depends(_service),
) -> Response:
    """GET /reports/generate — генерация или получение кэшированного отчёта.

    Возвращает StreamingResponse с файлом (Excel или PDF).
    """
    # Build params dict (exclude None values)
    params: dict = {}
    for key, value in {
        "project_id": project_id, "year": year, "month": month,
        "month_from": month_from, "month_to": month_to,
        "contract_type": contract_type,
        "income_contract_id": income_contract_id,
        "ls_id": ls_id, "journal_id": journal_id,
        "report_id": report_id, "status": status,
        "date_from": date_from, "date_to": date_to,
        "level": level,
    }.items():
        if value is not None:
            params[key] = value

    try:
        file_bytes, filename, content_type = await service.generate(type, params)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации отчёта: {exc}")

    # Write to temp file for streaming (aiofiles-compatible pattern)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix)
    tmp.write(file_bytes)
    tmp.close()
    background_tasks.add_task(_cleanup_temp, tmp.name)

    import aiofiles

    async def _stream():
        async with aiofiles.open(tmp.name, "rb") as f:
            while chunk := await f.read(1_048_576):  # 1 MB chunks
                yield chunk

    return StreamingResponse(
        _stream(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(file_bytes)),
        },
    )


@router.get("/list")
async def list_reports(
    project_id: UUID | None = None,
    service: ReportService = Depends(_service),
) -> list[dict]:
    """GET /reports/list — список сгенерированных отчётов из ReportCache."""
    return await service.list_reports(project_id)


@router.delete("/{report_cache_id}", status_code=204)
async def delete_report(
    report_cache_id: UUID,
    service: ReportService = Depends(_service),
) -> None:
    """DELETE /reports/{id} — удалить из MinIO + ReportCache."""
    deleted = await service.delete_report(report_cache_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Отчёт не найден в кэше")
