from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.user import User
from app.schemas.auth import CurrentUserProfileUpdate, LoginRequest, TokenResponse
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
    "notarial_intelligence",
    "system_status",
    "configuracion",
]


class AuthenticatedUserWithPermissions(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    document_type: str | None = None
    document_number: str | None = None
    phone: str | None = None
    job_title: str | None = None
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


@router.put("/me", response_model=AuthenticatedUserWithPermissions)
def update_me(payload: CurrentUserProfileUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = load_user_with_permissions(db, current_user.id)
    full_name = payload.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El nombre completo es obligatorio.")
    password = payload.password.strip() if payload.password is not None else None
    if password is not None and password != "" and len(password) < 8:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La contraseña debe tener al menos 8 caracteres.")

    user.full_name = full_name
    user.phone = payload.phone.strip() if payload.phone and payload.phone.strip() else None
    user.job_title = payload.job_title.strip() if payload.job_title and payload.job_title.strip() else None
    if password:
        user.password_hash = get_password_hash(password)

    db.commit()
    db.refresh(user)
    refreshed_user = load_user_with_permissions(db, user.id)
    response = serialize_user(refreshed_user)
    response["permissions"] = build_permission_union(refreshed_user)
    return response
