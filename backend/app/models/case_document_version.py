from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseDocumentVersion(TimestampMixin, Base):
    __tablename__ = "case_document_versions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_document_id: Mapped[int] = mapped_column(ForeignKey("case_documents.id"), index=True)
    version_number: Mapped[int] = mapped_column(index=True)
    file_format: Mapped[str] = mapped_column(String(20), index=True)
    storage_path: Mapped[str] = mapped_column(String(400))
    original_filename: Mapped[str] = mapped_column(String(255))
    generated_from_template_id: Mapped[int | None] = mapped_column(ForeignKey("document_templates.id"), nullable=True)
    placeholder_snapshot_json: Mapped[str] = mapped_column(Text, default="{}")
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    document: Mapped["CaseDocument"] = relationship(back_populates="versions")
    generated_from_template: Mapped["DocumentTemplate | None"] = relationship()
    created_by_user: Mapped["User | None"] = relationship(back_populates="case_document_versions")
