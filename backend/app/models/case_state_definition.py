from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CaseStateDefinition(TimestampMixin, Base):
    __tablename__ = "case_state_definitions"
    __table_args__ = (
        UniqueConstraint("case_type", "code", name="uq_case_state_definitions_case_type_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_type: Mapped[str] = mapped_column(String(80), index=True)
    code: Mapped[str] = mapped_column(String(50), index=True)
    label: Mapped[str] = mapped_column(String(120))
    step_order: Mapped[int] = mapped_column(Integer, index=True)
    is_initial: Mapped[bool] = mapped_column(Boolean, default=False)
    is_terminal: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
