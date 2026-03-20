"""FastAPI router for Projects — CRUD + aggregate endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.projects.schemas import ProjectCreate, ProjectUpdate, ProjectRead, ProjectList
from app.modules.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def _service(session: AsyncSession = Depends(get_session)) -> ProjectService:
    return ProjectService(session)


@router.get("", response_model=list[ProjectList])
async def list_projects(
    skip: int = 0, limit: int = 100, service: ProjectService = Depends(_service)
):
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, service: ProjectService = Depends(_service)):
    project = await service.get_by_id(project_id)
    if not project:
        raise HTTPException(404, "Проект не найден")
    return project


@router.post("", response_model=ProjectRead, status_code=201)
async def create_project(data: ProjectCreate, service: ProjectService = Depends(_service)):
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: UUID, data: ProjectUpdate, service: ProjectService = Depends(_service)
):
    project = await service.update(project_id, data)
    if not project:
        raise HTTPException(404, "Проект не найден")
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: UUID, service: ProjectService = Depends(_service)):
    if not await service.delete(project_id):
        raise HTTPException(404, "Проект не найден")


# ── Aggregate endpoints ──────────────────────────────────────────

@router.get("/{project_id}/tree")
async def get_project_tree(project_id: UUID, service: ProjectService = Depends(_service)):
    """Раздел 6.2 — Иерархическое дерево смет (Recursive CTE)."""
    return await service.get_tree(project_id)


@router.get("/{project_id}/budget-summary")
async def get_budget_summary(project_id: UUID, service: ProjectService = Depends(_service)):
    """Раздел 6.3 — Финансовая аналитика по уровням иерархии."""
    return await service.get_budget_summary(project_id)


@router.get("/{project_id}/id-readiness")
async def get_id_readiness(project_id: UUID, service: ProjectService = Depends(_service)):
    """Раздел 6.4 — Дашборд готовности ИД."""
    return await service.get_id_readiness(project_id)


@router.get("/{project_id}/alerts")
async def get_alerts(project_id: UUID, service: ProjectService = Depends(_service)):
    """Раздел 8.7 — Панель уведомлений и рисков."""
    return await service.get_alerts(project_id)
