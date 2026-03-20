"""Service layer for Projects — business logic + aggregate endpoints.

Includes:
  - CRUD delegation to repository
  - GET /projects/{id}/tree (delegates to EstimateAggregateRepository)
  - GET /projects/{id}/budget-summary
  - GET /projects/{id}/id-readiness (Раздел 6.4)
  - GET /projects/{id}/alerts (Раздел 8.7)
"""

from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schemas import ProjectCreate, ProjectUpdate
from app.modules.estimates.repository import EstimateAggregateRepository


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProjectRepository(session)
        self.estimate_agg = EstimateAggregateRepository(session)

    # ── CRUD ─────────────────────────────────────────────────────
    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, project_id: UUID):
        return await self.repo.get_by_id(project_id)

    async def create(self, data: ProjectCreate):
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise ValueError(f"Проект с шифром '{data.code}' уже существует")
        return await self.repo.create(data)

    async def update(self, project_id: UUID, data: ProjectUpdate):
        return await self.repo.update(project_id, data)

    async def delete(self, project_id: UUID):
        return await self.repo.delete(project_id)

    # ── Aggregate endpoints ──────────────────────────────────────
    async def get_tree(self, project_id: UUID) -> list[dict]:
        """Раздел 6.2 — иерархическое дерево через Recursive CTE."""
        return await self.estimate_agg.get_project_tree(project_id)

    async def get_budget_summary(self, project_id: UUID) -> list[dict]:
        """Раздел 6.3 — финансовая аналитика по уровням."""
        return await self.estimate_agg.get_budget_summary(project_id)

    async def get_id_readiness(self, project_id: UUID) -> list[dict]:
        """Раздел 6.4 — дашборд готовности ИД.

        По каждому разделу чертежей: требуется АОСР / оформлено / % закрытия объёма.
        """
        query = text("""
            SELECT
                d.mark,
                COUNT(DISTINCT d.id) AS total_drawings,
                COUNT(DISTINCT CASE WHEN ab.id IS NOT NULL THEN d.id END) AS drawings_with_asbuilt,
                COUNT(DISTINCT ab.id) AS total_asbuilt,
                CASE
                    WHEN COUNT(DISTINCT d.id) > 0
                    THEN ROUND(
                        COUNT(DISTINCT CASE WHEN ab.id IS NOT NULL THEN d.id END) * 100.0
                        / COUNT(DISTINCT d.id), 2
                    )
                    ELSE 0
                END AS readiness_percent
            FROM drawings d
            LEFT JOIN asbuilt_drawing ad ON ad.drawing_id = d.id
            LEFT JOIN asbuilt_docs ab ON ab.id = ad.asbuilt_id
            WHERE d.project_id = :project_id
            GROUP BY d.mark
            ORDER BY d.mark
        """)
        result = await self.session.execute(query, {"project_id": str(project_id)})
        return [dict(row._mapping) for row in result]

    async def get_alerts(self, project_id: UUID) -> dict:
        """Раздел 8.7 — панель уведомлений и рисков.

        Returns aggregated alerts:
          - overdue_inspections: просроченные предписания
          - expiring_certificates: сертификаты с истекающим сроком (< 30 дней)
          - uncovered_ls: ЛС с нераспределёнными объёмами
          - negative_balance: статьи с перерасходом бюджета
        """
        today = date.today()
        threshold = today + timedelta(days=30)

        # 🔴 Просроченные предписания
        q_inspections = text("""
            SELECT id, number, description, planned_fix_date, status
            FROM inspections
            WHERE project_id = :pid
              AND status != 'CLOSED'
              AND planned_fix_date < :today
            ORDER BY planned_fix_date
        """)

        # 🟡 Сертификаты с истекающим сроком
        q_certificates = text("""
            SELECT mc.id, mc.name, mc.document_number, mc.expiry_date, mc.status
            FROM material_certificates mc
            JOIN specifications s ON s.id = mc.specification_id
            JOIN drawings d ON d.id = s.drawing_id
            WHERE d.project_id = :pid
              AND mc.expiry_date IS NOT NULL
              AND mc.expiry_date < :threshold
              AND mc.status != 'REJECTED'
            ORDER BY mc.expiry_date
        """)

        # 🟠 ЛС с нераспределёнными объёмами (SUM percentage < 100)
        q_uncovered = text("""
            SELECT le.id, le.code, le.name, le.total_amount,
                   COALESCE(SUM(lic.percentage), 0) AS distributed_pct,
                   le.total_amount * (100 - COALESCE(SUM(lic.percentage), 0)) / 100 AS uncovered_amount
            FROM local_estimates le
            JOIN local_estimate_bases leb ON leb.id = le.lsr_id
            JOIN object_estimates oe ON oe.id = leb.object_estimate_id
            JOIN summary_estimates se ON se.id = oe.summary_estimate_id
            LEFT JOIN ls_income_contract lic ON lic.ls_id = le.id
            WHERE se.project_id = :pid
            GROUP BY le.id, le.code, le.name, le.total_amount
            HAVING COALESCE(SUM(lic.percentage), 0) < 100
            ORDER BY le.code
        """)

        # 🔴 Перерасход бюджета (остаток < 0)
        q_negative = text("""
            SELECT ei.id, ei.code, ei.name, ei.amount_approved,
                   COALESCE(SUM(p.amount_fact), 0) AS amount_fact,
                   (ei.amount_approved - COALESCE(SUM(p.amount_fact), 0)) AS balance
            FROM estimate_items ei
            JOIN local_estimates le ON le.id = ei.ls_id
            JOIN local_estimate_bases leb ON leb.id = le.lsr_id
            JOIN object_estimates oe ON oe.id = leb.object_estimate_id
            JOIN summary_estimates se ON se.id = oe.summary_estimate_id
            LEFT JOIN progress p ON p.estimate_item_id = ei.id
            WHERE se.project_id = :pid
            GROUP BY ei.id, ei.code, ei.name, ei.amount_approved
            HAVING (ei.amount_approved - COALESCE(SUM(p.amount_fact), 0)) < 0
            ORDER BY (ei.amount_approved - COALESCE(SUM(p.amount_fact), 0))
        """)

        params = {"pid": str(project_id), "today": today, "threshold": threshold}

        r1 = await self.session.execute(q_inspections, params)
        r2 = await self.session.execute(q_certificates, params)
        r3 = await self.session.execute(q_uncovered, params)
        r4 = await self.session.execute(q_negative, params)

        return {
            "overdue_inspections": [dict(r._mapping) for r in r1],
            "expiring_certificates": [dict(r._mapping) for r in r2],
            "uncovered_ls": [dict(r._mapping) for r in r3],
            "negative_balance": [dict(r._mapping) for r in r4],
        }
