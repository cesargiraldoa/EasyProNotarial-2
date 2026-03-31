from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class NotaryCommercialActivity(TimestampMixin, Base):
    __tablename__ = "notary_commercial_activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int] = mapped_column(ForeignKey("notaries.id", ondelete="CASCADE"), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    management_type: Mapped[str] = mapped_column(String(60))
    comment: Mapped[str] = mapped_column(Text)
    responsible: Mapped[str] = mapped_column(String(120))
    responsible_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    result: Mapped[str | None] = mapped_column(String(160), nullable=True)
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    notary: Mapped["Notary"] = relationship(back_populates="commercial_activities")
    responsible_user: Mapped["User | None"] = relationship(
        back_populates="commercial_activities",
        foreign_keys=[responsible_user_id],
    )
