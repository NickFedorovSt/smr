"""Report schemas — ReportRequest, ReportType enum (22 types)."""

import enum
from uuid import UUID

from pydantic import BaseModel


class ReportType(str, enum.Enum):
    # Группа 1: Финансовые отчёты
    BUDGET_BALANCE = "BUDGET_BALANCE"
    BUDGET_BY_CONTRACTS = "BUDGET_BY_CONTRACTS"
    MONTHLY_PROGRESS = "MONTHLY_PROGRESS"
    QUARTERLY_PROGRESS = "QUARTERLY_PROGRESS"
    # Группа 2: Приёмочные формы
    KS2 = "KS2"
    KS3 = "KS3"
    KS6A = "KS6A"
    # Группа 3: Материальная отчётность
    M29_REPORT = "M29_REPORT"
    MATERIAL_DEMAND = "MATERIAL_DEMAND"
    # Группа 4: Статусы документации
    ID_REGISTRY = "ID_REGISTRY"
    ID_READINESS = "ID_READINESS"
    INSPECTION_REPORT = "INSPECTION_REPORT"
    CERTIFICATE_STATUS = "CERTIFICATE_STATUS"
    # Группа 5: Сроки и планирование
    SCHEDULE_DEVIATION = "SCHEDULE_DEVIATION"
    # Группа 6: Журналы СДО
    WORK_JOURNAL_PRINT = "WORK_JOURNAL_PRINT"
    INPUT_CONTROL_JOURNAL = "INPUT_CONTROL_JOURNAL"
    # Группа 7: Договорные отчёты
    CONTRACT_REGISTRY = "CONTRACT_REGISTRY"
    MARGIN_REPORT = "MARGIN_REPORT"
    UNCOVERED_LS = "UNCOVERED_LS"
    # Группа 8: Управленческие отчёты
    EXECUTIVE_DASHBOARD = "EXECUTIVE_DASHBOARD"
    MULTI_PROJECT_SUMMARY = "MULTI_PROJECT_SUMMARY"


class ReportRequest(BaseModel):
    report_type: ReportType
    project_id: UUID | None = None
    # Additional optional params — will be extended per report type
    year: int | None = None
    month: int | None = None
    month_from: int | None = None
    month_to: int | None = None
    contract_type: str | None = None  # INCOME | EXPENSE | ALL
    income_contract_id: UUID | None = None
    ls_id: UUID | None = None
    journal_id: UUID | None = None
    report_id: UUID | None = None
    status: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    level: str | None = None  # SSR | OSR | LSR | LS
