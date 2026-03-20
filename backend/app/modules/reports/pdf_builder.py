"""PDF report base class + child classes (ReportLab Platypus + Drawing).

Base class: PdfReport
  Methods: add_title(), add_requisites_table(), add_work_table(),
  add_pie_chart(), add_progress_bar(), add_signatures_block(), build_to_bytes()

Child classes: KS2Report, KS3Report, WorkJournalReport, ExecutiveDashboardReport
"""

from __future__ import annotations

import io
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Any, Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Register a Cyrillic-capable font (Helvetica is built-in, but for full Cyrillic
# we rely on ReportLab's built-in handling; for production, register a TTF font).

_STYLES = getSampleStyleSheet()
_TITLE_STYLE = ParagraphStyle(
    "ReportTitle",
    parent=_STYLES["Title"],
    fontSize=14,
    leading=18,
    alignment=TA_CENTER,
    spaceAfter=6 * mm,
)
_SUBTITLE_STYLE = ParagraphStyle(
    "ReportSubtitle",
    parent=_STYLES["Normal"],
    fontSize=10,
    leading=13,
    alignment=TA_CENTER,
    spaceAfter=4 * mm,
)
_NORMAL = ParagraphStyle(
    "ReportNormal",
    parent=_STYLES["Normal"],
    fontSize=9,
    leading=12,
)
_BOLD = ParagraphStyle(
    "ReportBold",
    parent=_NORMAL,
    fontName="Helvetica-Bold",
)
_RIGHT = ParagraphStyle(
    "ReportRight",
    parent=_NORMAL,
    alignment=TA_RIGHT,
)

_TABLE_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
])


def _fmt(value: Any) -> str:
    """Format a value for PDF cells."""
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return f"{value:,.2f}"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")
    return str(value)


# ═══════════════════════════════════════════════════════════════
# Helper: execute text() query
# ═══════════════════════════════════════════════════════════════

async def _fetch(session: Any, sql: str, params: dict[str, Any]) -> list[dict]:
    from sqlalchemy import text

    result = await session.execute(text(sql), params)
    return [dict(row) for row in result.mappings().all()]


# ═══════════════════════════════════════════════════════════════
# Base class
# ═══════════════════════════════════════════════════════════════

class PdfReport(ABC):
    """Reusable base for every ReportLab-based report."""

    def __init__(self) -> None:
        self.elements: list[Any] = []

    # ── helpers ──────────────────────────────────────────────

    def add_title(self, title: str, subtitle: str | None = None) -> None:
        self.elements.append(Paragraph(title, _TITLE_STYLE))
        if subtitle:
            self.elements.append(Paragraph(subtitle, _SUBTITLE_STYLE))
        self.elements.append(Spacer(1, 4 * mm))

    def add_requisites_table(self, rows: list[tuple[str, str]]) -> None:
        """Two-column table for document requisites (label: value)."""
        data = [[Paragraph(f"<b>{label}</b>", _NORMAL), Paragraph(value, _NORMAL)]
                for label, value in rows]
        t = Table(data, colWidths=[6 * cm, 12 * cm])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        self.elements.append(t)
        self.elements.append(Spacer(1, 6 * mm))

    def add_work_table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        col_widths: list[float] | None = None,
    ) -> None:
        """Standard data table with header row."""
        data = [headers] + [[_fmt(c) for c in row] for row in rows]
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(_TABLE_STYLE)
        self.elements.append(t)
        self.elements.append(Spacer(1, 4 * mm))

    def add_totals_row(self, label: str, values: list[Any]) -> None:
        """Bold totals row below a table."""
        row = [Paragraph(f"<b>{label}</b>", _NORMAL)] + [
            Paragraph(f"<b>{_fmt(v)}</b>", _RIGHT) for v in values
        ]
        t = Table([row], colWidths=None)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2F3")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        self.elements.append(t)
        self.elements.append(Spacer(1, 4 * mm))

    def add_pie_chart(
        self,
        data: list[float],
        labels: list[str],
        title: str = "",
        width: float = 200,
        height: float = 150,
    ) -> None:
        """Embedded pie chart via reportlab.graphics."""
        d = Drawing(width, height)
        pie = Pie()
        pie.x = 30
        pie.y = 10
        pie.width = 120
        pie.height = 120
        pie.data = data
        pie.labels = labels
        pie.slices.strokeWidth = 0.5
        chart_colors = [
            colors.HexColor("#4472C4"),
            colors.HexColor("#ED7D31"),
            colors.HexColor("#A5A5A5"),
            colors.HexColor("#FFC000"),
            colors.HexColor("#70AD47"),
        ]
        for i in range(len(data)):
            pie.slices[i].fillColor = chart_colors[i % len(chart_colors)]
        d.add(pie)
        if title:
            d.add(String(width / 2, height - 5, title,
                         textAnchor="middle", fontSize=9, fontName="Helvetica-Bold"))
        self.elements.append(d)
        self.elements.append(Spacer(1, 4 * mm))

    def add_progress_bar(
        self, value: float, max_val: float = 100, label: str = ""
    ) -> None:
        """Simple horizontal progress bar."""
        pct = min(value / max_val, 1.0) if max_val > 0 else 0
        bar_width = 14 * cm
        bar_height = 0.6 * cm

        d = Drawing(bar_width + 3 * cm, bar_height + 0.4 * cm)
        # Background
        d.add(
            Drawing._fillAndStroke(  # type: ignore[attr-defined]
                d, colors.HexColor("#E0E0E0"), None, 0, 0, bar_width, bar_height
            )
            if False
            else Drawing(0, 0)  # placeholder — use Rect from shapes
        )
        from reportlab.graphics.shapes import Rect

        d.add(Rect(0, 0, bar_width, bar_height,
                    fillColor=colors.HexColor("#E0E0E0"), strokeColor=None))
        d.add(Rect(0, 0, bar_width * pct, bar_height,
                    fillColor=colors.HexColor("#4472C4"), strokeColor=None))
        pct_text = f"{value:.1f}%"
        if label:
            pct_text = f"{label}: {pct_text}"
        d.add(String(bar_width + 0.3 * cm, bar_height / 3, pct_text,
                      fontSize=8, fontName="Helvetica"))
        self.elements.append(d)
        self.elements.append(Spacer(1, 3 * mm))

    def add_signatures_block(self, roles: list[tuple[str, str]]) -> None:
        """Signature block: [(role, name), ...]."""
        self.elements.append(Spacer(1, 10 * mm))
        data = []
        for role, name in roles:
            data.append([
                Paragraph(role, _BOLD),
                "____________",
                Paragraph(name, _NORMAL),
            ])
        t = Table(data, colWidths=[6 * cm, 4 * cm, 6 * cm])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        self.elements.append(t)

    def build_to_bytes(self) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
        )
        doc.build(self.elements)
        buf.seek(0)
        return buf.read()

    # ── abstract ──────────────────────────────────────────────

    @abstractmethod
    async def build(self, session: Any, params: dict[str, Any]) -> bytes:
        """Generate report bytes. Accepts AsyncSession + params dict."""


# ═══════════════════════════════════════════════════════════════
# KS2 — Акт о приёмке выполненных работ
# ═══════════════════════════════════════════════════════════════

class KS2Report(PdfReport):
    """PDF: КС-2 — Постановление Госкомстата РФ № 100 от 11.11.1999."""

    async def build(self, session: Any, params: dict[str, Any]) -> bytes:
        project_id = str(params["project_id"])
        income_contract_id = str(params["income_contract_id"])
        period_month = params["month"]
        period_year = params["year"]

        # Project + contract info
        meta = await _fetch(session, """
            SELECT
                p.name AS project_name, p.customer, p.contractor,
                ic.number AS contract_number, ic.name AS contract_name,
                ic.counterparty
            FROM projects p
            JOIN income_contracts ic ON ic.project_id = p.id
            WHERE p.id = :project_id AND ic.id = :contract_id
        """, {"project_id": project_id, "contract_id": income_contract_id})

        info = meta[0] if meta else {}

        # Work items for the period
        rows = await _fetch(session, """
            SELECT
                ROW_NUMBER() OVER (ORDER BY ei.code) AS num,
                ei.name, ei.unit,
                p.volume_fact, ei.amount_approved / NULLIF(ei.volume_approved, 0) AS unit_price,
                p.amount_fact
            FROM progress p
            JOIN estimate_items ei ON ei.id = p.estimate_item_id
            JOIN local_estimates le ON le.id = ei.ls_id
            JOIN ls_income_contract lic ON lic.ls_id = le.id
            WHERE lic.income_contract_id = :contract_id
              AND p.year = :year AND p.month = :month
            ORDER BY ei.code
        """, {
            "contract_id": income_contract_id,
            "year": period_year,
            "month": period_month,
        })

        # Build PDF
        self.add_title(
            "АКТ О ПРИЁМКЕ ВЫПОЛНЕННЫХ РАБОТ",
            f"(форма КС-2)",
        )

        self.add_requisites_table([
            ("Объект:", info.get("project_name", "")),
            ("Заказчик:", info.get("customer", "")),
            ("Подрядчик:", info.get("contractor", "")),
            ("Договор:", f"{info.get('contract_number', '')} — {info.get('contract_name', '')}"),
            ("Отчётный период:", f"{period_month:02d}.{period_year}"),
        ])

        headers = ["№", "Наименование работ", "Ед. изм.", "Кол-во", "Цена", "Сумма"]
        table_rows = []
        total_amount = Decimal(0)
        for r in rows:
            amount = r.get("amount_fact") or Decimal(0)
            total_amount += amount if isinstance(amount, Decimal) else Decimal(str(amount))
            table_rows.append([
                r.get("num"), r.get("name"), r.get("unit"),
                r.get("volume_fact"), r.get("unit_price"), amount,
            ])

        col_w = [1.2 * cm, 7 * cm, 2 * cm, 2.5 * cm, 2.5 * cm, 3 * cm]
        self.add_work_table(headers, table_rows, col_widths=col_w)
        self.add_totals_row("ИТОГО:", [total_amount])

        self.add_signatures_block([
            ("Сдал (Подрядчик):", info.get("contractor", "")),
            ("Принял (Заказчик):", info.get("customer", "")),
        ])

        return self.build_to_bytes()


# ═══════════════════════════════════════════════════════════════
# KS3 — Справка о стоимости выполненных работ
# ═══════════════════════════════════════════════════════════════

class KS3Report(PdfReport):
    """PDF: КС-3 — Справка о стоимости выполненных работ."""

    async def build(self, session: Any, params: dict[str, Any]) -> bytes:
        project_id = str(params["project_id"])
        income_contract_id = str(params["income_contract_id"])
        period_month = params["month"]
        period_year = params["year"]

        meta = await _fetch(session, """
            SELECT
                p.name AS project_name, p.customer, p.contractor,
                ic.number AS contract_number, ic.total_amount AS contract_amount
            FROM projects p
            JOIN income_contracts ic ON ic.project_id = p.id
            WHERE p.id = :project_id AND ic.id = :contract_id
        """, {"project_id": project_id, "contract_id": income_contract_id})

        info = meta[0] if meta else {}

        # Three sums: from_start, from_year_start, for_period
        rows = await _fetch(session, """
            SELECT
                COALESCE(SUM(p.amount_fact), 0) AS from_start,
                COALESCE(SUM(CASE WHEN p.year = :year THEN p.amount_fact ELSE 0 END), 0) AS from_year,
                COALESCE(SUM(CASE WHEN p.year = :year AND p.month = :month
                             THEN p.amount_fact ELSE 0 END), 0) AS for_period
            FROM progress p
            JOIN estimate_items ei ON ei.id = p.estimate_item_id
            JOIN local_estimates le ON le.id = ei.ls_id
            JOIN ls_income_contract lic ON lic.ls_id = le.id
            WHERE lic.income_contract_id = :contract_id
        """, {
            "contract_id": income_contract_id,
            "year": period_year,
            "month": period_month,
        })

        sums = rows[0] if rows else {}

        self.add_title(
            "СПРАВКА О СТОИМОСТИ ВЫПОЛНЕННЫХ РАБОТ И ЗАТРАТ",
            "(форма КС-3)",
        )

        self.add_requisites_table([
            ("Объект:", info.get("project_name", "")),
            ("Заказчик:", info.get("customer", "")),
            ("Подрядчик:", info.get("contractor", "")),
            ("Договор:", info.get("contract_number", "")),
            ("Стоимость по договору:", _fmt(info.get("contract_amount"))),
            ("Отчётный период:", f"{period_month:02d}.{period_year}"),
        ])

        headers = ["Наименование", "С начала строительства", "С начала года", "За отчётный период"]
        table_rows = [[
            "Стоимость выполненных работ",
            sums.get("from_start"), sums.get("from_year"), sums.get("for_period"),
        ]]

        col_w = [5 * cm, 4 * cm, 4 * cm, 4 * cm]
        self.add_work_table(headers, table_rows, col_widths=col_w)

        self.add_signatures_block([
            ("Сдал (Подрядчик):", info.get("contractor", "")),
            ("Принял (Заказчик):", info.get("customer", "")),
        ])

        return self.build_to_bytes()


# ═══════════════════════════════════════════════════════════════
# M29 PDF — Печатная форма М-29
# ═══════════════════════════════════════════════════════════════

class M29PdfReport(PdfReport):
    """PDF: M29 — Печатная форма для подписания прорабом."""

    async def build(self, session: Any, params: dict[str, Any]) -> bytes:
        report_id = str(params.get("report_id") or "")
        project_id = str(params.get("project_id", ""))

        if report_id:
            where = "mr.id = :report_id"
            qp: dict[str, Any] = {"report_id": report_id}
        else:
            where = "mr.project_id = :project_id AND mr.period_month = :month AND mr.period_year = :year"
            qp = {"project_id": project_id, "month": params["month"], "year": params["year"]}

        rows = await _fetch(session, f"""
            SELECT
                s.name AS material, s.mark_standard, ml.unit,
                ml.norm_consumption, ml.actual_consumption, ml.deviation,
                mr.foreman_name, mr.period_month, mr.period_year,
                p.name AS project_name
            FROM m29_lines ml
            JOIN m29_reports mr ON mr.id = ml.report_id
            JOIN specifications s ON s.id = ml.specification_id
            JOIN projects p ON p.id = mr.project_id
            WHERE {where}
            ORDER BY s.position
        """, qp)

        info = rows[0] if rows else {}
        period = f"{info.get('period_month', '')}/{info.get('period_year', '')}"

        self.add_title("ОТЧЁТ О РАСХОДЕ МАТЕРИАЛОВ (Форма М-29)")
        self.add_requisites_table([
            ("Объект:", info.get("project_name", "")),
            ("Период:", period),
            ("Прораб:", info.get("foreman_name", "")),
        ])

        headers = ["Материал", "ГОСТ/ТУ", "Ед.", "Норма", "Факт", "Откл."]
        table_rows = [
            [r["material"], r.get("mark_standard"), r["unit"],
             r["norm_consumption"], r["actual_consumption"], r["deviation"]]
            for r in rows
        ]
        self.add_work_table(headers, table_rows,
                            col_widths=[5 * cm, 3 * cm, 1.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm])

        self.add_signatures_block([
            ("Прораб:", info.get("foreman_name", "")),
        ])

        return self.build_to_bytes()


# ═══════════════════════════════════════════════════════════════
# WorkJournalReport — Общий журнал работ (ОЖР)
# ═══════════════════════════════════════════════════════════════

class WorkJournalReport(PdfReport):
    """PDF: ОЖР — РД-11-05-2007, Приказ Минстроя № 1026/пр."""

    async def build(self, session: Any, params: dict[str, Any]) -> bytes:
        journal_id = str(params["journal_id"])
        qp: dict[str, Any] = {"journal_id": journal_id}
        filt = ""
        if params.get("date_from"):
            filt += " AND je.entry_date >= :date_from::date"
            qp["date_from"] = params["date_from"]
        if params.get("date_to"):
            filt += " AND je.entry_date <= :date_to::date"
            qp["date_to"] = params["date_to"]

        meta = await _fetch(session, """
            SELECT wj.name, wj.type, wj.started_date,
                   p.name AS project_name, p.customer, p.contractor
            FROM work_journals wj
            JOIN projects p ON p.id = wj.project_id
            WHERE wj.id = :journal_id
        """, {"journal_id": journal_id})

        info = meta[0] if meta else {}

        entries = await _fetch(session, f"""
            SELECT je.entry_date, je.description, je.responsible
            FROM journal_entries je
            WHERE je.journal_id = :journal_id {filt}
            ORDER BY je.entry_date
        """, qp)

        self.add_title("ОБЩИЙ ЖУРНАЛ РАБОТ (ОЖР)")
        self.add_requisites_table([
            ("Объект:", info.get("project_name", "")),
            ("Журнал:", info.get("name", "")),
            ("Заказчик:", info.get("customer", "")),
            ("Подрядчик:", info.get("contractor", "")),
            ("Дата начала:", _fmt(info.get("started_date"))),
        ])

        headers = ["Дата", "Описание работ", "Ответственный"]
        table_rows = [
            [r["entry_date"], r["description"], r["responsible"]]
            for r in entries
        ]
        self.add_work_table(headers, table_rows,
                            col_widths=[2.5 * cm, 12 * cm, 4 * cm])

        self.add_signatures_block([
            ("Руководитель:", ""),
            ("Технадзор:", ""),
        ])

        return self.build_to_bytes()


# ═══════════════════════════════════════════════════════════════
# ExecutiveDashboardReport — Сводный управленческий отчёт (1 стр. А4)
# ═══════════════════════════════════════════════════════════════

class ExecutiveDashboardReport(PdfReport):
    """PDF: Сводный управленческий отчёт (1 страница А4).

    5 блоков: общие сведения, финансы (Pie), сроки, ИД прогресс, предписания.
    """

    async def build(self, session: Any, params: dict[str, Any]) -> bytes:
        project_id = str(params["project_id"])

        # Block 1: общие сведения
        info_rows = await _fetch(session, """
            SELECT name, customer, contractor,
                   planned_start, planned_end, actual_start, actual_end, status
            FROM projects WHERE id = :pid
        """, {"pid": project_id})
        info = info_rows[0] if info_rows else {}

        # Block 2: финансы
        fin_rows = await _fetch(session, """
            SELECT
                COALESCE(SUM(se.total_amount), 0) AS budget,
                COALESCE(fact.total_fact, 0) AS fact
            FROM summary_estimates se
            LEFT JOIN LATERAL (
                SELECT SUM(pr.amount_fact) AS total_fact
                FROM progress pr
                JOIN estimate_items ei ON ei.id = pr.estimate_item_id
                JOIN local_estimates le ON le.id = ei.ls_id
                JOIN local_estimate_bases leb ON leb.id = le.lsr_id
                JOIN object_estimates oe ON oe.id = leb.object_estimate_id
                WHERE oe.summary_estimate_id = se.id
            ) fact ON TRUE
            WHERE se.project_id = :pid
            GROUP BY fact.total_fact
        """, {"pid": project_id})
        fin = fin_rows[0] if fin_rows else {"budget": 0, "fact": 0}
        budget = float(fin.get("budget") or 0)
        fact = float(fin.get("fact") or 0)
        remaining = budget - fact
        budget_pct = (fact / budget * 100) if budget > 0 else 0

        # Block 4: ИД готовность
        id_rows = await _fetch(session, """
            SELECT
                COUNT(DISTINCT d.id) AS total_d,
                COUNT(DISTINCT CASE WHEN ad.status = 'SIGNED' THEN ad.id END) AS signed_d
            FROM drawings d
            LEFT JOIN asbuilt_drawing abd ON abd.drawing_id = d.id
            LEFT JOIN asbuilt_docs ad ON ad.id = abd.asbuilt_doc_id
            WHERE d.project_id = :pid
        """, {"pid": project_id})
        id_info = id_rows[0] if id_rows else {"total_d": 0, "signed_d": 0}
        total_d = int(id_info.get("total_d") or 0)
        signed_d = int(id_info.get("signed_d") or 0)
        id_pct = (signed_d / total_d * 100) if total_d > 0 else 0

        # Block 5: предписания
        insp_rows = await _fetch(session, """
            SELECT
                COUNT(*) FILTER (WHERE status = 'OPEN') AS open_count,
                COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') AS in_progress,
                COUNT(*) FILTER (WHERE status != 'CLOSED'
                    AND planned_fix_date < CURRENT_DATE) AS overdue
            FROM inspections WHERE project_id = :pid
        """, {"pid": project_id})
        insp = insp_rows[0] if insp_rows else {}

        # ── Build PDF ──
        self.add_title(
            "СВОДНЫЙ УПРАВЛЕНЧЕСКИЙ ОТЧЁТ",
            info.get("name", ""),
        )

        # Block 1
        self.add_requisites_table([
            ("Заказчик:", info.get("customer", "")),
            ("Подрядчик:", info.get("contractor", "")),
            ("Плановый период:", f"{_fmt(info.get('planned_start'))} — {_fmt(info.get('planned_end'))}"),
            ("Статус:", info.get("status", "")),
        ])

        # Block 2: Pie chart
        pie_data = [fact, remaining] if remaining >= 0 else [fact, 0]
        pie_labels = [
            f"Факт: {_fmt(fact)} руб.",
            f"Остаток: {_fmt(remaining)} руб.",
        ]
        self.add_pie_chart(pie_data, pie_labels, title=f"Бюджет: выполнено {budget_pct:.1f}%",
                           width=280, height=160)

        # Block 3: Сроки — простая таблица
        self.add_work_table(
            ["Показатель", "Значение"],
            [
                ["Плановая дата завершения", _fmt(info.get("planned_end"))],
                ["Фактический старт", _fmt(info.get("actual_start"))],
            ],
            col_widths=[8 * cm, 6 * cm],
        )

        # Block 4: Progress bar ИД
        self.add_progress_bar(id_pct, 100, label="Готовность ИД")

        # Block 5: Предписания
        self.add_work_table(
            ["Открыто", "В работе", "Просрочено"],
            [[insp.get("open_count", 0), insp.get("in_progress", 0), insp.get("overdue", 0)]],
            col_widths=[4 * cm, 4 * cm, 4 * cm],
        )

        return self.build_to_bytes()


# ═══════════════════════════════════════════════════════════════
# Registry: ReportType → PdfReport subclass
# ═══════════════════════════════════════════════════════════════

PDF_BUILDERS: dict[str, type[PdfReport]] = {
    "KS2": KS2Report,
    "KS3": KS3Report,
    "M29_REPORT": M29PdfReport,
    "WORK_JOURNAL_PRINT": WorkJournalReport,
    "EXECUTIVE_DASHBOARD": ExecutiveDashboardReport,
}
