from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseDocument(TimestampMixin, Base):
    __tablename__ = "case_documents"
    __table_args__ = (UniqueConstraint("case_id", "category", name="uq_case_document_category"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(160))
    current_version_number: Mapped[int] = mapped_column(default=0)

    case: Mapped["Case"] = relationship(back_populates="documents")
    versions: Mapped[list["CaseDocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="desc(CaseDocumentVersion.version_number)",
    )
