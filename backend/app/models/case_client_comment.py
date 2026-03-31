from __future__ import annotations

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseClientComment(TimestampMixin, Base):
    __tablename__ = "case_client_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    comment: Mapped[str] = mapped_column(Text)

    case: Mapped["Case"] = relationship(back_populates="client_comments")
    created_by_user: Mapped["User | None"] = relationship(back_populates="client_case_comments")
