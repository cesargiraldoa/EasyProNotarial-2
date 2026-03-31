from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class NotaryCrmAuditLog(TimestampMixin, Base):
    __tablename__ = "notary_crm_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int] = mapped_column(ForeignKey("notaries.id", ondelete="CASCADE"), index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    field_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    notary: Mapped["Notary"] = relationship(back_populates="crm_audit_logs")
    actor_user: Mapped["User | None"] = relationship(
        back_populates="crm_audit_logs",
        foreign_keys=[actor_user_id],
    )
