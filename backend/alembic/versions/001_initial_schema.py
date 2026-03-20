"""Initial schema — all tables, CHECK constraints, indexes, GENERATED COLUMN.

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ────────────────────────────────────────────────────────────
    # ENUM types
    # ────────────────────────────────────────────────────────────
    project_status = postgresql.ENUM(
        "DESIGN", "CONSTRUCTION", "COMMISSIONING", "COMPLETED",
        name="project_status", create_type=True,
    )
    expertise_status = postgresql.ENUM(
        "NOT_SUBMITTED", "SUBMITTED", "APPROVED", "REVISION_REQUIRED",
        name="expertise_status", create_type=True,
    )
    local_estimate_type = postgresql.ENUM(
        "MAIN", "ADDITIONAL",
        name="local_estimate_type", create_type=True,
    )
    contract_status = postgresql.ENUM(
        "DRAFT", "ACTIVE", "COMPLETED", "TERMINATED",
        name="contract_status", create_type=True,
    )
    drawing_status = postgresql.ENUM(
        "DRAFT", "ISSUED", "REVISION", "CANCELLED",
        name="drawing_status", create_type=True,
    )
    entity_type = postgresql.ENUM(
        "DRAWING", "ASBUILT", "CERTIFICATE", "M29", "INSPECTION", "REPORT", "OTHER",
        name="entity_type", create_type=True,
    )
    asbuilt_type = postgresql.ENUM(
        "AOSR", "AOOK", "EXEC_SCHEME",
        name="asbuilt_type", create_type=True,
    )
    asbuilt_status = postgresql.ENUM(
        "DRAFT", "SIGNED", "ACCEPTED",
        name="asbuilt_status", create_type=True,
    )
    journal_type = postgresql.ENUM(
        "GENERAL", "SPECIAL",
        name="journal_type", create_type=True,
    )
    certificate_status = postgresql.ENUM(
        "PENDING", "APPROVED", "REJECTED",
        name="certificate_status", create_type=True,
    )
    m29_status = postgresql.ENUM(
        "DRAFT", "SUBMITTED", "APPROVED",
        name="m29_status", create_type=True,
    )
    inspection_status = postgresql.ENUM(
        "OPEN", "IN_PROGRESS", "CLOSED",
        name="inspection_status", create_type=True,
    )
    inspection_entity_type = postgresql.ENUM(
        "DRAWING", "ASBUILT", "ESTIMATE_ITEM",
        name="inspection_entity_type", create_type=True,
    )

    # Create all enum types
    for enum_type in [
        project_status, expertise_status, local_estimate_type,
        contract_status, drawing_status, entity_type,
        asbuilt_type, asbuilt_status, journal_type,
        certificate_status, m29_status, inspection_status,
        inspection_entity_type,
    ]:
        enum_type.create(op.get_bind(), checkfirst=True)

    # ════════════════════════════════════════════════════════════
    # 4.1 PROJECTS
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("customer", sa.String(500)),
        sa.Column("contractor", sa.String(500)),
        sa.Column("planned_start", sa.Date),
        sa.Column("planned_end", sa.Date),
        sa.Column("actual_start", sa.Date),
        sa.Column("actual_end", sa.Date),
        sa.Column("status", project_status, server_default="DESIGN"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # ════════════════════════════════════════════════════════════
    # 4.2 ESTIMATE HIERARCHY
    # ════════════════════════════════════════════════════════════

    # ── ССР ──
    op.create_table(
        "summary_estimates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("expertise_status", expertise_status, server_default="NOT_SUBMITTED"),
        sa.Column("expertise_date", sa.Date),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_summary_estimates_project_id", "summary_estimates", ["project_id"])

    # ── ОСР ──
    op.create_table(
        "object_estimates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("summary_estimate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("summary_estimates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("expertise_status", expertise_status, server_default="NOT_SUBMITTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_object_estimates_summary_estimate_id", "object_estimates", ["summary_estimate_id"])

    # ── ЛСР ──
    op.create_table(
        "local_estimate_bases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("object_estimate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("object_estimates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("price_index", sa.Numeric(10, 4), nullable=False),
        sa.Column("expertise_status", expertise_status, server_default="NOT_SUBMITTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_local_estimate_bases_object_estimate_id", "local_estimate_bases", ["object_estimate_id"])

    # ── ЛС ──
    op.create_table(
        "local_estimates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lsr_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("local_estimate_bases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("type", local_estimate_type, server_default="MAIN"),
        sa.Column("total_amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("price_index", sa.Numeric(10, 4)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_local_estimates_lsr_id", "local_estimates", ["lsr_id"])

    # ── EstimateItem ──
    op.create_table(
        "estimate_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ls_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("local_estimates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("volume_approved", sa.Numeric(18, 4), server_default="0"),
        sa.Column("amount_approved", sa.Numeric(18, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_estimate_items_ls_id", "estimate_items", ["ls_id"])

    # ════════════════════════════════════════════════════════════
    # 4.3 CONTRACTS
    # ════════════════════════════════════════════════════════════

    # ── IncomeContract ──
    op.create_table(
        "income_contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("number", sa.String(100), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("counterparty", sa.String(500), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("status", contract_status, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_income_contracts_project_id", "income_contracts", ["project_id"])

    # ── ExpenseContract ──
    op.create_table(
        "expense_contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("number", sa.String(100), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("counterparty", sa.String(500), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("status", contract_status, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_expense_contracts_project_id", "expense_contracts", ["project_id"])

    # ── ls_income_contract (M2M) ──
    op.create_table(
        "ls_income_contract",
        sa.Column("ls_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("local_estimates.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("income_contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("income_contracts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("percentage", sa.Numeric(5, 2), nullable=False),
    )
    op.create_check_constraint("ck_ls_income_percentage", "ls_income_contract", "percentage >= 0 AND percentage <= 100")
    op.create_index("ix_ls_income_contract_ls_id", "ls_income_contract", ["ls_id"])
    op.create_index("ix_ls_income_contract_income_contract_id", "ls_income_contract", ["income_contract_id"])

    # ── income_expense_contract (M2M) ──
    op.create_table(
        "income_expense_contract",
        sa.Column("income_contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("income_contracts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("expense_contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("expense_contracts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("percentage", sa.Numeric(5, 2), nullable=False),
    )
    op.create_check_constraint("ck_income_expense_percentage", "income_expense_contract", "percentage >= 0 AND percentage <= 100")
    op.create_index("ix_income_expense_income_id", "income_expense_contract", ["income_contract_id"])
    op.create_index("ix_income_expense_expense_id", "income_expense_contract", ["expense_contract_id"])

    # ════════════════════════════════════════════════════════════
    # 4.4 DRAWINGS
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "drawings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mark", sa.String(20), nullable=False),
        sa.Column("sheet_number", sa.String(50), nullable=False),
        sa.Column("revision", sa.String(10), server_default="0"),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("status", drawing_status, server_default="DRAFT"),
        sa.Column("issued_date", sa.Date),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_drawings_project_id", "drawings", ["project_id"])

    op.create_table(
        "specifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("drawing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("drawings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.String(20), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("mark_standard", sa.String(200)),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("volume_designed", sa.Numeric(18, 4), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_specifications_drawing_id", "specifications", ["drawing_id"])

    # ── ls_drawing (M2M) ──
    op.create_table(
        "ls_drawing",
        sa.Column("ls_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("local_estimates.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("drawing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("drawings.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_ls_drawing_ls_id", "ls_drawing", ["ls_id"])
    op.create_index("ix_ls_drawing_drawing_id", "ls_drawing", ["drawing_id"])

    # ════════════════════════════════════════════════════════════
    # 4.5 DOCUMENTS
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", entity_type, nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.BigInteger, nullable=False),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("checksum", sa.String(32)),
        sa.Column("uploaded_by", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_documents_entity", "documents", ["entity_type", "entity_id"])

    # ════════════════════════════════════════════════════════════
    # 4.6 PROGRESS
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("estimate_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("estimate_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("month", sa.Integer, nullable=False),
        sa.Column("volume_fact", sa.Numeric(18, 4), server_default="0"),
        sa.Column("amount_fact", sa.Numeric(18, 2), server_default="0"),
        sa.Column("ks2_number", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    # Explicit CHECK constraint (Раздел 5 п.1)
    op.create_check_constraint("ck_progress_month", "progress", "month >= 1 AND month <= 12")
    # Required index (Раздел 5 п.3)
    op.create_index("idx_progress_item_period", "progress", ["estimate_item_id", "year", "month"])

    # ════════════════════════════════════════════════════════════
    # 4.7 AS-BUILT DOCUMENTATION
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "asbuilt_docs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", asbuilt_type, nullable=False),
        sa.Column("number", sa.String(100), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("work_date", sa.Date, nullable=False),
        sa.Column("sign_date", sa.Date, nullable=False),
        sa.Column("foreman", sa.String(200), nullable=False),
        sa.Column("supervisor", sa.String(200), nullable=False),
        sa.Column("status", asbuilt_status, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_asbuilt_docs_project_id", "asbuilt_docs", ["project_id"])

    # ── asbuilt_drawing (M2M) ──
    op.create_table(
        "asbuilt_drawing",
        sa.Column("asbuilt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asbuilt_docs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("drawing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("drawings.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_asbuilt_drawing_asbuilt_id", "asbuilt_drawing", ["asbuilt_id"])
    op.create_index("ix_asbuilt_drawing_drawing_id", "asbuilt_drawing", ["drawing_id"])

    # ── asbuilt_specification (M2M with volume_closed) ──
    op.create_table(
        "asbuilt_specification",
        sa.Column("asbuilt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asbuilt_docs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("specification_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("specifications.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("volume_closed", sa.Numeric(18, 4), nullable=False, server_default="0"),
    )
    op.create_index("ix_asbuilt_spec_asbuilt_id", "asbuilt_specification", ["asbuilt_id"])
    op.create_index("ix_asbuilt_spec_specification_id", "asbuilt_specification", ["specification_id"])

    # ── WorkJournal ──
    op.create_table(
        "work_journals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", journal_type, nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("started_date", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_work_journals_project_id", "work_journals", ["project_id"])

    # ── JournalEntry ──
    op.create_table(
        "journal_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("journal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_journals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entry_date", sa.Date, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("responsible", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_journal_entries_journal_id", "journal_entries", ["journal_id"])

    # ════════════════════════════════════════════════════════════
    # 4.8 MATERIAL CERTIFICATES
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "material_certificates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("specification_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("specifications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("document_number", sa.String(100), nullable=False),
        sa.Column("standard", sa.String(200)),
        sa.Column("issue_date", sa.Date, nullable=False),
        sa.Column("expiry_date", sa.Date),
        sa.Column("status", certificate_status, server_default="PENDING"),
        sa.Column("rejection_reason", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_material_certificates_specification_id", "material_certificates", ["specification_id"])

    # ════════════════════════════════════════════════════════════
    # 4.9 M29
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "m29_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period_month", sa.Integer, nullable=False),
        sa.Column("period_year", sa.Integer, nullable=False),
        sa.Column("foreman_name", sa.String(200), nullable=False),
        sa.Column("status", m29_status, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_check_constraint("ck_m29_month", "m29_reports", "period_month >= 1 AND period_month <= 12")
    op.create_index("ix_m29_reports_project_id", "m29_reports", ["project_id"])

    # ── M29Line with GENERATED COLUMN (Раздел 5 п.4) ──
    op.create_table(
        "m29_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("m29_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("specification_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("specifications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("norm_consumption", sa.Numeric(18, 4), server_default="0"),
        sa.Column("actual_consumption", sa.Numeric(18, 4), server_default="0"),
        sa.Column(
            "deviation",
            sa.Numeric(18, 4),
            sa.Computed("actual_consumption - norm_consumption", persisted=True),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_m29_lines_report_id", "m29_lines", ["report_id"])
    op.create_index("ix_m29_lines_specification_id", "m29_lines", ["specification_id"])

    # ════════════════════════════════════════════════════════════
    # 4.10 INSPECTIONS
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "inspections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("number", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("norm_reference", sa.String(500)),
        sa.Column("planned_fix_date", sa.Date, nullable=False),
        sa.Column("actual_fix_date", sa.Date),
        sa.Column("status", inspection_status, server_default="OPEN"),
        sa.Column("related_entity_type", inspection_entity_type),
        sa.Column("related_entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_inspections_project_id", "inspections", ["project_id"])

    op.create_table(
        "inspection_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("old_status", inspection_status, nullable=False),
        sa.Column("new_status", inspection_status, nullable=False),
        sa.Column("comment", sa.String(2000)),
        sa.Column("changed_by", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_inspection_logs_inspection_id", "inspection_logs", ["inspection_id"])

    # ════════════════════════════════════════════════════════════
    # 4.11 REPORT CACHE
    # ════════════════════════════════════════════════════════════
    op.create_table(
        "report_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("params_hash", sa.String(32), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    # Required unique index (Раздел 5 п.3)
    op.create_index("idx_report_cache_lookup", "report_cache", ["report_type", "params_hash"], unique=True)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    tables = [
        "report_cache",
        "inspection_logs", "inspections",
        "m29_lines", "m29_reports",
        "material_certificates",
        "journal_entries", "work_journals",
        "asbuilt_specification", "asbuilt_drawing", "asbuilt_docs",
        "progress",
        "documents",
        "ls_drawing", "specifications", "drawings",
        "income_expense_contract", "ls_income_contract",
        "expense_contracts", "income_contracts",
        "estimate_items", "local_estimates", "local_estimate_bases",
        "object_estimates", "summary_estimates",
        "projects",
    ]
    for table in tables:
        op.drop_table(table)

    # Drop enum types
    enums = [
        "inspection_entity_type", "inspection_status",
        "m29_status", "certificate_status",
        "journal_type", "asbuilt_status", "asbuilt_type",
        "entity_type", "drawing_status", "contract_status",
        "local_estimate_type", "expertise_status", "project_status",
    ]
    for enum_name in enums:
        postgresql.ENUM(name=enum_name).drop(op.get_bind(), checkfirst=True)
