"""Repository for Project CRUD operations."""

from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.models import Project
from app.modules.projects.schemas import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Project]:
        result = await self.session.execute(
            select(Project).offset(skip).limit(limit).order_by(Project.code)
        )
        return list(result.scalars().all())

    async def get_by_id(self, project_id: UUID) -> Project | None:
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Project | None:
        result = await self.session.execute(
            select(Project).where(Project.code == code)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ProjectCreate) -> Project:
        project = Project(**data.model_dump())
        self.session.add(project)
        await self.session.flush()
        return project

    async def update(self, project_id: UUID, data: ProjectUpdate) -> Project | None:
        project = await self.get_by_id(project_id)
        if not project:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        await self.session.flush()
        return project

    async def delete(self, project_id: UUID) -> bool:
        result = await self.session.execute(
            delete(Project).where(Project.id == project_id)
        )
        return result.rowcount > 0
