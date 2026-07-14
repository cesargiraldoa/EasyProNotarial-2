from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
import sqlalchemy as sa
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
    print(f"[biblioteca/campos] user_id={current_user.id} notary_id={notary_id}")
    # Construir SQL nativo para evitar bugs de ORM con IS NULL en OR
    conditions = ["is_active = true"]
    params: dict = {}

    if notary_id is None:
        conditions.append("scope = 'global' AND notary_id IS NULL")
    else:
        conditions.append("(scope = 'global' AND notary_id IS NULL) OR (scope = 'notary' AND notary_id = :notary_id)")
        params["notary_id"] = notary_id

    if category:
        conditions.append("category = :category")
        params["category"] = category.strip()
    if scope:
        conditions.append("scope = :scope")
        params["scope"] = scope.strip()
    if search:
        conditions.append("(code ILIKE :search OR label ILIKE :search)")
        params["search"] = f"%{search.strip()}%"

    where = " AND ".join(conditions)
    sql = sa.text(f"""
        SELECT * FROM notarial_field_catalog
        WHERE {where}
        ORDER BY CASE WHEN scope = 'global' THEN 0 ELSE 1 END,
                 category ASC, code ASC
    """)

    rows = db.execute(sql, params).mappings().all()
    print(f"[biblioteca/campos] resultados={len(rows)}")
    return [NotarialFieldCatalog(**dict(row)) for row in rows]
