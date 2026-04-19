from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import RolePermissionItem, UserRoleAssignmentSummary
from app.services.auth import AuthenticationError, authenticate_user, build_login_response, serialize_user

router = APIRouter(prefix="/auth", tags=["auth"])


MODULE_CODES = [
    "resumen",
    "comercial",
    "notarias",
    "usuarios",
    "roles",
    "minutas",
    "crear_minuta",
    "actos_plantillas",
    "lotes",
    "system_status",
    "configuracion",
]


class AuthenticatedUserWithPermissions(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    roles: list[str]
    role_codes: list[str]
    permissions: list[RolePermissionItem]
    default_notary: str | None = None
    assignments: list[UserRoleAssignmentSummary] = Field(default_factory=list)


def load_user_with_permissions(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role).joinedload(Role.permissions),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return user


def build_permission_union(user: User) -> list[RolePermissionItem]:
    permission_map = {module_code: False for module_code in MODULE_CODES}
    for assignment in user.role_assignments:
        for permission in assignment.role.permissions:
            if permission.module_code not in permission_map:
                permission_map[permission.module_code] = False
            permission_map[permission.module_code] = permission_map[permission.module_code] or permission.can_access
    ordered_module_codes = list(MODULE_CODES)
    for module_code in sorted(permission_map):
        if module_code not in ordered_module_codes:
            ordered_module_codes.append(module_code)
    return [RolePermissionItem(module_code=module_code, can_access=permission_map[module_code]) for module_code in ordered_module_codes]


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, payload.email, payload.password)
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    return build_login_response(user)


@router.get("/me", response_model=AuthenticatedUserWithPermissions)
def me(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = load_user_with_permissions(db, current_user.id)
    payload = serialize_user(user)
    payload["permissions"] = build_permission_union(user)
    return payload
