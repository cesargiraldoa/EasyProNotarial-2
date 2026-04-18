from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, get_role_codes, require_roles
from app.core.security import get_password_hash
from app.models.notary import Notary
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.user import User
from app.schemas.user import (
    RoleCatalogItem,
    UserCreate,
    UserDetail,
    UserOption,
    UserRoleAssignmentSummary,
    UserStatusUpdate,
    UserSummary,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


ROLE_ORDER = ["super_admin", "admin_notary", "notary", "approver", "protocolist", "client"]


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


def get_assignable_roles(db: Session, current_user: User) -> list[Role]:
    query = db.query(Role)
    if not has_role(current_user, "super_admin"):
        query = query.filter(Role.code != "super_admin")
    roles = query.all()
    return sorted(roles, key=lambda role: ROLE_ORDER.index(role.code) if role.code in ROLE_ORDER else 999)


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


@router.get("/options", response_model=list[UserOption])
def list_user_options(
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(User).options(joinedload(User.default_notary)).order_by(User.full_name.asc())
    if active_only:
        query = query.filter(User.is_active.is_(True))
    users = query.all()
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
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
    if db.query(User).filter(User.email == payload.email).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un usuario con ese correo.")

    if payload.default_notary_id is not None:
        if db.query(Notary.id).filter(Notary.id == payload.default_notary_id).first() is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría por defecto no existe.")
        if not has_role(current_user, "super_admin") and payload.default_notary_id not in get_manageable_notary_ids(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar usuarios a esa notaría.")

    user = User(
        email=str(payload.email).lower(),
        full_name=payload.full_name.strip(),
        password_hash=get_password_hash(payload.password),
        is_active=payload.is_active,
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

    duplicate = db.query(User).filter(User.email == payload.email, User.id != user.id).first()
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe otro usuario con ese correo.")

    if payload.default_notary_id is not None:
        if db.query(Notary.id).filter(Notary.id == payload.default_notary_id).first() is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría por defecto no existe.")
        if not has_role(current_user, "super_admin") and payload.default_notary_id not in get_manageable_notary_ids(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar usuarios a esa notaría.")

    user.email = str(payload.email).lower()
    user.full_name = payload.full_name.strip()
    user.is_active = payload.is_active
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
