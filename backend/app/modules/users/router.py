from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, get_role_codes, has_role, require_roles
from app.core.security import get_password_hash
from app.models.notary import Notary
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.role_permission import RolePermission
from app.models.user import User
from app.schemas.user import (
    RoleCreate,
    RoleCatalogItem,
    RolePermissionItem,
    RoleUpdate,
    UserCreate,
    UserDetail,
    UserOption,
    UserRoleAssignmentSummary,
    UserStatusUpdate,
    UserSummary,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


ROLE_ORDER = ["super_admin", "admin_notary", "notary", "notary_titular", "notary_suplente", "approver", "protocolist", "client"]
DOCUMENT_TYPE_CODES = {"CC", "CE", "PA", "NIT", "OTRO"}
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


def serialize_assignment(assignment: RoleAssignment) -> UserRoleAssignmentSummary:
    return UserRoleAssignmentSummary(
        id=assignment.id,
        role_id=assignment.role_id,
        role_code=assignment.role.code,
        role_name=assignment.role.name,
        notary_id=assignment.notary_id,
        notary_label=assignment.notary.notary_label if assignment.notary else None,
    )


def serialize_user(user: User) -> UserSummary:
    assignment_names = []
    for assignment in user.role_assignments:
        suffix = f" ({assignment.notary.notary_label})" if assignment.notary else ""
        assignment_names.append(f"{assignment.role.name}{suffix}")

    return UserSummary(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        document_type=user.document_type,
        document_number=user.document_number,
        phone=user.phone,
        job_title=user.job_title,
        default_notary_id=user.default_notary_id,
        default_notary_label=user.default_notary.notary_label if user.default_notary else None,
        roles=assignment_names,
        assignments=[serialize_assignment(assignment) for assignment in user.role_assignments],
    )


def load_user_or_404(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return user


def get_manageable_notary_ids(user: User) -> set[int]:
    ids: set[int] = set()
    if user.default_notary_id is not None:
        ids.add(user.default_notary_id)
    for assignment in user.role_assignments or []:
        if assignment.notary_id is not None:
            ids.add(assignment.notary_id)
    return ids


def normalize_document_type(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    return normalized or None


def normalize_document_number(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def normalize_email(value: str) -> str:
    return value.strip().lower()


def ensure_unique_user_identity(db: Session, document_type: str | None, document_number: str | None, user_id: int | None = None) -> None:
    if document_type is None or document_number is None:
        return
    query = db.query(User.id).filter(
        User.document_type == document_type,
        User.document_number == document_number,
    )
    if user_id is not None:
        query = query.filter(User.id != user_id)
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe otro usuario con ese tipo y número de identificación.",
        )


def get_assignable_roles(db: Session, current_user: User) -> list[Role]:
    query = db.query(Role)
    if not has_role(current_user, "super_admin"):
        query = query.filter(Role.code != "super_admin")
    roles = query.all()
    return sorted(roles, key=lambda role: ROLE_ORDER.index(role.code) if role.code in ROLE_ORDER else 999)


def load_role_or_404(db: Session, role_id: int) -> Role:
    role = (
        db.query(Role)
        .options(joinedload(Role.permissions))
        .filter(Role.id == role_id)
        .first()
    )
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    return role


def serialize_role_permissions(role: Role) -> list[RolePermissionItem]:
    permission_map = {permission.module_code: permission.can_access for permission in role.permissions}
    ordered_module_codes = list(MODULE_CODES)
    for module_code in sorted(permission_map):
        if module_code not in ordered_module_codes:
            ordered_module_codes.append(module_code)
    return [
        RolePermissionItem(
            module_code=module_code,
            can_access=permission_map.get(module_code, False),
        )
        for module_code in ordered_module_codes
    ]


def ensure_assignment_permissions(current_user: User, role: Role, notary_id: int | None) -> None:
    manageable_notary_ids = get_manageable_notary_ids(current_user)
    if role.code == "super_admin" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo SuperAdmin puede asignar ese rol.")
    if role.scope == "notary":
        if notary_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El rol {role.name} requiere notaría asociada.")
        if has_role(current_user, "super_admin"):
            return
        if notary_id not in manageable_notary_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar roles fuera de tus notarías.")
    elif role.scope == "global" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar roles globales.")


def sync_assignments(db: Session, user: User, payload_assignments, current_user: User) -> None:
    role_map = {role.code: role for role in db.query(Role).all()}
    normalized_pairs: set[tuple[int, int | None]] = set()
    db.query(RoleAssignment).filter(RoleAssignment.user_id == user.id).delete(synchronize_session=False)
    db.flush()

    for assignment_payload in payload_assignments:
        role = role_map.get(assignment_payload.role_code)
        if role is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Rol desconocido: {assignment_payload.role_code}")
        ensure_assignment_permissions(current_user, role, assignment_payload.notary_id)
        pair = (role.id, assignment_payload.notary_id)
        if pair in normalized_pairs:
            continue
        normalized_pairs.add(pair)
        db.add(
            RoleAssignment(
                user_id=user.id,
                role_id=role.id,
                notary_id=assignment_payload.notary_id if role.scope == "notary" else None,
            )
        )
    db.flush()


@router.get("/roles", response_model=list[RoleCatalogItem])
def list_roles(db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    return get_assignable_roles(db, current_user)


@router.post("/roles", response_model=RoleCatalogItem, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    code = payload.code.strip()
    name = payload.name.strip()
    scope = payload.scope.strip()
    description = payload.description.strip()

    if code == "super_admin" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo SuperAdmin puede crear ese rol.")
    if db.query(Role.id).filter(Role.code == code).first() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ya existe un rol con ese code.")
    if db.query(Role.id).filter(Role.name == name).first() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ya existe un rol con ese nombre.")
    role = Role(
        code=code,
        name=name,
        scope=scope,
        description=description,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.patch("/roles/{role_id}", response_model=RoleCatalogItem)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    if role.code == "super_admin" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo SuperAdmin puede editar ese rol.")
    duplicate_name = db.query(Role.id).filter(Role.name == payload.name.strip(), Role.id != role.id).first()
    if duplicate_name is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ya existe un rol con ese nombre.")
    role.name = payload.name.strip()
    role.description = payload.description.strip()
    db.commit()
    db.refresh(role)
    return role


@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    if role.code == "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se puede eliminar el rol super_admin.")
    if db.query(RoleAssignment.id).filter(RoleAssignment.role_id == role.id).first() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No se puede eliminar un rol con usuarios asignados.")
    db.delete(role)
    db.commit()
    return {"deleted": True}


@router.get("/roles/{role_id}/permissions", response_model=list[RolePermissionItem])
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin_notary")),
):
    role = load_role_or_404(db, role_id)
    return serialize_role_permissions(role)


@router.put("/roles/{role_id}/permissions", response_model=list[RolePermissionItem])
def update_role_permissions(
    role_id: int,
    payload: list[RolePermissionItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin_notary")),
):
    role = load_role_or_404(db, role_id)
    if role.code == "super_admin" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo SuperAdmin puede modificar esos permisos.")

    existing_permissions = {permission.module_code: permission for permission in role.permissions}
    normalized_payload: dict[str, RolePermissionItem] = {}
    for item in payload:
        normalized_payload[item.module_code] = item

    for item in normalized_payload.values():
        current_permission = existing_permissions.get(item.module_code)
        if current_permission is None:
            db.add(
                RolePermission(
                    role_id=role.id,
                    module_code=item.module_code,
                    can_access=item.can_access,
                )
            )
        else:
            current_permission.can_access = item.can_access

    db.commit()
    role = load_role_or_404(db, role.id)
    return serialize_role_permissions(role)


@router.get("/options", response_model=list[UserOption])
def list_user_options(
    active_only: bool = Query(default=True),
    role_code: str | None = Query(default=None),
    notary_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role_codes = get_role_codes(current_user)
    query = db.query(User).options(joinedload(User.default_notary)).order_by(User.full_name.asc())
    if "super_admin" not in role_codes:
        query = query.filter(User.default_notary_id == current_user.default_notary_id)
    elif notary_id is not None:
        query = query.filter(User.default_notary_id == notary_id)

    def apply_role_filter(base_query, requested_role_code: str | None):
        if not requested_role_code:
            return base_query
        filtered_query = (
            base_query.join(User.role_assignments)
            .join(RoleAssignment.role)
            .filter(Role.code == requested_role_code)
        )
        if notary_id is not None:
            filtered_query = filtered_query.filter(RoleAssignment.notary_id == notary_id)
        return filtered_query.distinct()

    def finalize(base_query):
        final_query = base_query
        if active_only:
            final_query = final_query.filter(User.is_active.is_(True))
        return final_query.all()

    if role_code == "notary_titular":
        titular_users = finalize(apply_role_filter(query, "notary_titular"))
        if titular_users:
            users = titular_users
        else:
            users = finalize(apply_role_filter(query, "notary"))
    else:
        users = finalize(apply_role_filter(query, role_code))
    return [
        UserOption(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            default_notary_id=user.default_notary_id,
            default_notary_label=user.default_notary.notary_label if user.default_notary else None,
        )
        for user in users
    ]


@router.get("", response_model=list[UserSummary])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "notary"))):
    role_codes = get_role_codes(current_user)
    query = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .order_by(User.full_name.asc())
    )
    if "super_admin" not in role_codes:
        query = query.filter(User.default_notary_id == current_user.default_notary_id)
    return [serialize_user(user) for user in query.all()]


@router.get("/{user_id}", response_model=UserDetail)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    user = load_user_or_404(db, user_id)
    if not has_role(current_user, "super_admin"):
        manageable_notary_ids = get_manageable_notary_ids(current_user)
        visible = user.default_notary_id in manageable_notary_ids or any(
            assignment.notary_id in manageable_notary_ids for assignment in user.role_assignments if assignment.notary_id is not None
        )
        if not visible:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para ver este usuario.")
    return serialize_user(user)


@router.post("", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    email = normalize_email(payload.email)
    document_type = normalize_document_type(payload.document_type)
    document_number = normalize_document_number(payload.document_number)

    if document_type is None or document_number is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El tipo y número de identificación son obligatorios para crear usuarios.")
    ensure_unique_user_identity(db, document_type, document_number)
    if db.query(User).filter(User.email == email).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un usuario con ese correo.")

    if payload.default_notary_id is not None:
        if db.query(Notary.id).filter(Notary.id == payload.default_notary_id).first() is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría por defecto no existe.")
        if not has_role(current_user, "super_admin") and payload.default_notary_id not in get_manageable_notary_ids(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar usuarios a esa notaría.")

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=get_password_hash(payload.password),
        is_active=payload.is_active,
        document_type=document_type,
        document_number=document_number,
        phone=payload.phone.strip() if payload.phone else None,
        job_title=payload.job_title.strip() if payload.job_title else None,
        default_notary_id=payload.default_notary_id,
    )
    db.add(user)
    db.flush()
    sync_assignments(db, user, payload.assignments, current_user)
    db.commit()
    return serialize_user(load_user_or_404(db, user.id))


@router.put("/{user_id}", response_model=UserDetail)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    user = load_user_or_404(db, user_id)

    if not has_role(current_user, "super_admin"):
        manageable_notary_ids = get_manageable_notary_ids(current_user)
        visible = user.default_notary_id in manageable_notary_ids or any(
            assignment.notary_id in manageable_notary_ids for assignment in user.role_assignments if assignment.notary_id is not None
        )
        if not visible:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para editar este usuario.")

    email = normalize_email(payload.email)
    document_type = normalize_document_type(payload.document_type)
    document_number = normalize_document_number(payload.document_number)

    duplicate = db.query(User).filter(User.email == email, User.id != user.id).first()
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe otro usuario con ese correo.")
    ensure_unique_user_identity(db, document_type, document_number, user.id)

    if payload.default_notary_id is not None:
        if db.query(Notary.id).filter(Notary.id == payload.default_notary_id).first() is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría por defecto no existe.")
        if not has_role(current_user, "super_admin") and payload.default_notary_id not in get_manageable_notary_ids(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar usuarios a esa notaría.")

    user.email = email
    user.full_name = payload.full_name.strip()
    user.is_active = payload.is_active
    user.document_type = document_type
    user.document_number = document_number
    user.phone = payload.phone.strip() if payload.phone else None
    user.job_title = payload.job_title.strip() if payload.job_title else None
    user.default_notary_id = payload.default_notary_id
    if payload.password:
        user.password_hash = get_password_hash(payload.password)

    sync_assignments(db, user, payload.assignments, current_user)
    db.commit()
    return serialize_user(load_user_or_404(db, user.id))


@router.patch("/{user_id}/status", response_model=UserDetail)
def update_user_status(user_id: int, payload: UserStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    user = load_user_or_404(db, user_id)
    if not has_role(current_user, "super_admin"):
        manageable_notary_ids = get_manageable_notary_ids(current_user)
        visible = user.default_notary_id in manageable_notary_ids or any(
            assignment.notary_id in manageable_notary_ids for assignment in user.role_assignments if assignment.notary_id is not None
        )
        if not visible:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para actualizar este usuario.")
    user.is_active = payload.is_active
    db.commit()
    return serialize_user(load_user_or_404(db, user.id))
