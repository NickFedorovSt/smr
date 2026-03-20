"""Repository for Estimate hierarchy — CRUD + Recursive CTE + budget aggregation.

Key features:
  - Recursive CTE for GET /projects/{id}/tree (Раздел 6.2)
  - Financial aggregation for GET /projects/{id}/budget-summary (Раздел 6.3)
  - NO Python loops / N+1 — all aggregation in SQL
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, delete, text, func, literal_column, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.estimates.models import (
    SummaryEstimate,
    ObjectEstimate,
    LocalEstimateBase,
    LocalEstimate,
    EstimateItem,
)
from app.modules.estimates.schemas import (
    SummaryEstimateCreate, SummaryEstimateUpdate,
    ObjectEstimateCreate, ObjectEstimateUpdate,
    LocalEstimateBaseCreate, LocalEstimateBaseUpdate,
    LocalEstimateCreate, LocalEstimateUpdate,
    EstimateItemCreate, EstimateItemUpdate,
)
from app.modules.progress.models import Progress


# ══════════════════════════════════════════════════════════════════
# Generic CRUD mixin
# ══════════════════════════════════════════════════════════════════
class _CrudMixin:
    """Reusable CRUD operations for a given model class."""

    def __init__(self, session: AsyncSession, model_class):
        self.session = session
        self.model_class = model_class

    async def get_all(self, skip: int = 0, limit: int = 100, **filters):
        stmt = select(self.model_class)
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model_class, field) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: UUID):
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data):
        entity = self.model_class(**data.model_dump())
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity_id: UUID, data):
        entity = await self.get_by_id(entity_id)
        if not entity:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, field, value)
        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.session.execute(
            delete(self.model_class).where(self.model_class.id == entity_id)
        )
        return result.rowcount > 0


# ══════════════════════════════════════════════════════════════════
# Individual repositories
# ══════════════════════════════════════════════════════════════════
class SummaryEstimateRepository(_CrudMixin):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SummaryEstimate)

    async def get_by_project(self, project_id: UUID) -> list[SummaryEstimate]:
        return await self.get_all(project_id=project_id)


class ObjectEstimateRepository(_CrudMixin):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ObjectEstimate)

    async def get_by_summary(self, summary_estimate_id: UUID) -> list[ObjectEstimate]:
        return await self.get_all(summary_estimate_id=summary_estimate_id)


class LocalEstimateBaseRepository(_CrudMixin):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LocalEstimateBase)

    async def get_by_object(self, object_estimate_id: UUID) -> list[LocalEstimateBase]:
        return await self.get_all(object_estimate_id=object_estimate_id)


class LocalEstimateRepository(_CrudMixin):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LocalEstimate)

    async def get_by_lsr(self, lsr_id: UUID) -> list[LocalEstimate]:
        return await self.get_all(lsr_id=lsr_id)


class EstimateItemRepository(_CrudMixin):
    def __init__(self, session: AsyncSession):
        super().__init__(session, EstimateItem)

    async def get_by_ls(self, ls_id: UUID) -> list[EstimateItem]:
        return await self.get_all(ls_id=ls_id)


# ══════════════════════════════════════════════════════════════════
# Aggregate queries — Recursive CTE + budget summary
# ══════════════════════════════════════════════════════════════════
class EstimateAggregateRepository:
    """Complex queries: tree view and budget aggregation.

    All aggregation performed in SQL — no Python loops or N+1.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_project_tree(self, project_id: UUID) -> list[dict]:
        """Recursive CTE for full estimate hierarchy (Раздел 6.2).

        Returns flat list with level/parent info for client-side tree building.
        Uses WITH RECURSIVE — NO Python loops.
        """
        query = text("""
            WITH RECURSIVE estimate_tree AS (
                -- Anchor: ССР (top level)
                SELECT
                    se.id,
                    se.code,
                    se.name,
                    'SSR' AS level,
                    se.total_amount,
                    se.project_id AS parent_id,
                    NULL::uuid AS parent_node_id,
                    1 AS depth
                FROM summary_estimates se
                WHERE se.project_id = :project_id

                UNION ALL

                -- ОСР
                SELECT
                    oe.id,
                    oe.code,
                    oe.name,
                    'OSR' AS level,
                    oe.total_amount,
                    oe.summary_estimate_id AS parent_id,
                    et.id AS parent_node_id,
                    et.depth + 1
                FROM object_estimates oe
                JOIN estimate_tree et ON et.id = oe.summary_estimate_id AND et.level = 'SSR'

                UNION ALL

                -- ЛСР
                SELECT
                    leb.id,
                    leb.code,
                    leb.name,
                    'LSR' AS level,
                    leb.total_amount,
                    leb.object_estimate_id AS parent_id,
                    et.id AS parent_node_id,
                    et.depth + 1
                FROM local_estimate_bases leb
                JOIN estimate_tree et ON et.id = leb.object_estimate_id AND et.level = 'OSR'

                UNION ALL

                -- ЛС
                SELECT
                    le.id,
                    le.code,
                    le.name,
                    'LS' AS level,
                    le.total_amount,
                    le.lsr_id AS parent_id,
                    et.id AS parent_node_id,
                    et.depth + 1
                FROM local_estimates le
                JOIN estimate_tree et ON et.id = le.lsr_id AND et.level = 'LSR'

                UNION ALL

                -- Сметные статьи
                SELECT
                    ei.id,
                    ei.code,
                    ei.name,
                    'ITEM' AS level,
                    ei.amount_approved AS total_amount,
                    ei.ls_id AS parent_id,
                    et.id AS parent_node_id,
                    et.depth + 1
                FROM estimate_items ei
                JOIN estimate_tree et ON et.id = ei.ls_id AND et.level = 'LS'
            )
            SELECT
                et.id,
                et.code,
                et.name,
                et.level,
                et.total_amount,
                et.parent_node_id,
                et.depth,
                COALESCE(fact.amount_fact, 0) AS amount_fact
            FROM estimate_tree et
            LEFT JOIN LATERAL (
                SELECT SUM(p.amount_fact) AS amount_fact
                FROM progress p
                WHERE et.level = 'ITEM' AND p.estimate_item_id = et.id
            ) fact ON TRUE
            ORDER BY et.depth, et.code
        """)

        result = await self.session.execute(query, {"project_id": str(project_id)})
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    async def get_budget_summary(self, project_id: UUID) -> list[dict]:
        """Budget summary with aggregation at each level (Раздел 6.3).

        Остаток = amount_approved - SUM(amount_fact)
        Aggregates: EstimateItem → ЛС → ЛСР → ОСР → ССР
        Uses func.sum() + group_by() with JOIN по иерархии.
        """
        query = text("""
            WITH item_facts AS (
                -- Факт по каждой сметной статье
                SELECT
                    ei.id AS item_id,
                    ei.ls_id,
                    ei.code AS item_code,
                    ei.name AS item_name,
                    ei.amount_approved,
                    COALESCE(SUM(p.amount_fact), 0) AS amount_fact
                FROM estimate_items ei
                LEFT JOIN progress p ON p.estimate_item_id = ei.id
                JOIN local_estimates le ON le.id = ei.ls_id
                JOIN local_estimate_bases leb ON leb.id = le.lsr_id
                JOIN object_estimates oe ON oe.id = leb.object_estimate_id
                JOIN summary_estimates se ON se.id = oe.summary_estimate_id
                WHERE se.project_id = :project_id
                GROUP BY ei.id, ei.ls_id, ei.code, ei.name, ei.amount_approved
            ),
            ls_summary AS (
                SELECT
                    le.id,
                    le.code,
                    le.name,
                    'LS' AS level,
                    le.total_amount AS amount_approved,
                    COALESCE(SUM(itf.amount_fact), 0) AS amount_fact
                FROM local_estimates le
                JOIN local_estimate_bases leb ON leb.id = le.lsr_id
                JOIN object_estimates oe ON oe.id = leb.object_estimate_id
                JOIN summary_estimates se ON se.id = oe.summary_estimate_id
                LEFT JOIN item_facts itf ON itf.ls_id = le.id
                WHERE se.project_id = :project_id
                GROUP BY le.id, le.code, le.name, le.total_amount
            ),
            lsr_summary AS (
                SELECT
                    leb.id,
                    leb.code,
                    leb.name,
                    'LSR' AS level,
                    leb.total_amount AS amount_approved,
                    COALESCE(SUM(ls.amount_fact), 0) AS amount_fact
                FROM local_estimate_bases leb
                JOIN object_estimates oe ON oe.id = leb.object_estimate_id
                JOIN summary_estimates se ON se.id = oe.summary_estimate_id
                LEFT JOIN ls_summary ls ON ls.id IN (
                    SELECT le2.id FROM local_estimates le2 WHERE le2.lsr_id = leb.id
                )
                WHERE se.project_id = :project_id
                GROUP BY leb.id, leb.code, leb.name, leb.total_amount
            ),
            osr_summary AS (
                SELECT
                    oe.id,
                    oe.code,
                    oe.name,
                    'OSR' AS level,
                    oe.total_amount AS amount_approved,
                    COALESCE(SUM(lsr.amount_fact), 0) AS amount_fact
                FROM object_estimates oe
                JOIN summary_estimates se ON se.id = oe.summary_estimate_id
                LEFT JOIN lsr_summary lsr ON lsr.id IN (
                    SELECT leb2.id FROM local_estimate_bases leb2 WHERE leb2.object_estimate_id = oe.id
                )
                WHERE se.project_id = :project_id
                GROUP BY oe.id, oe.code, oe.name, oe.total_amount
            ),
            ssr_summary AS (
                SELECT
                    se.id,
                    se.code,
                    se.name,
                    'SSR' AS level,
                    se.total_amount AS amount_approved,
                    COALESCE(SUM(osr.amount_fact), 0) AS amount_fact
                FROM summary_estimates se
                LEFT JOIN osr_summary osr ON osr.id IN (
                    SELECT oe2.id FROM object_estimates oe2 WHERE oe2.summary_estimate_id = se.id
                )
                WHERE se.project_id = :project_id
                GROUP BY se.id, se.code, se.name, se.total_amount
            )
            SELECT id, code, name, level, amount_approved, amount_fact,
                   (amount_approved - amount_fact) AS amount_remaining,
                   CASE WHEN amount_approved > 0
                        THEN ROUND(amount_fact * 100.0 / amount_approved, 2)
                        ELSE 0
                   END AS percent_complete
            FROM (
                SELECT * FROM ssr_summary
                UNION ALL SELECT * FROM osr_summary
                UNION ALL SELECT * FROM lsr_summary
                UNION ALL SELECT * FROM ls_summary
            ) combined
            ORDER BY level, code
        """)

        result = await self.session.execute(query, {"project_id": str(project_id)})
        rows = result.mappings().all()
        return [dict(row) for row in rows]
