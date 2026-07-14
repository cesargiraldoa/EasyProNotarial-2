from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import case, or_
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.notarial_field_catalog import NotarialFieldCatalog
from app.models.user import User


router = APIRouter(prefix="/biblioteca", tags=["biblioteca"])


class FieldCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    label: str
    field_type: str
    category: str
    description: str | None = None
    options_json: str | None = None
    scope: str
    notary_id: int | None = None


@router.get("/campos", response_model=list[FieldCatalogItem])
def list_field_catalog(
    category: str | None = Query(default=None),
    scope: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notary_id = current_user.default_notary_id
    query = db.query(NotarialFieldCatalog).filter(NotarialFieldCatalog.is_active.is_(True))

    if notary_id is None:
        query = query.filter(NotarialFieldCatalog.scope == "global", NotarialFieldCatalog.notary_id.is_(None))
    else:
        query = query.filter(
            or_(
                (NotarialFieldCatalog.scope == "global") & NotarialFieldCatalog.notary_id.is_(None),
                (NotarialFieldCatalog.scope == "notary") & (NotarialFieldCatalog.notary_id == notary_id),
            )
        )

    if category:
        query = query.filter(NotarialFieldCatalog.category == category.strip())
    if scope:
        query = query.filter(NotarialFieldCatalog.scope == scope.strip())
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(or_(NotarialFieldCatalog.code.ilike(pattern), NotarialFieldCatalog.label.ilike(pattern)))

    scope_order = case((NotarialFieldCatalog.scope == "global", 0), else_=1)
    return query.order_by(scope_order, NotarialFieldCatalog.category.asc(), NotarialFieldCatalog.code.asc()).all()
