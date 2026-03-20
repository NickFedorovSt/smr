"""Progress model — 4.6 ПОМЕСЯЧНЫЙ ФАКТ (КС-2).

Monthly actual work volumes and amounts per EstimateItem.
"""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (
        CheckConstraint("month >= 1 AND month <= 12", name="ck_progress_month"),
        Index("idx_progress_item_period", "estimate_item_id", "year", "month"),
    )

    estimate_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("estimate_items.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    volume_fact: Mapped[float] = mapped_column(Numeric(18, 4), default=0)
    amount_fact: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    ks2_number: Mapped[str | None] = mapped_column(String(100))

    # Relationships
    estimate_item = relationship("EstimateItem", back_populates="progress_entries")
