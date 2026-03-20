"""ReportCache model — 4.11 КЭШ ОТЧЁТОВ.

Cached generated reports stored in MinIO.
"""

from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReportCache(Base):
    __tablename__ = "report_cache"
    __table_args__ = (
        Index("idx_report_cache_lookup", "report_type", "params_hash", unique=True),
    )

    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    params_hash: Mapped[str] = mapped_column(String(32), nullable=False)  # md5
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)  # MinIO path
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
