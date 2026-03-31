from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.security import ALGORITHM
from app.db.session import SessionLocal
from app.models.role_assignment import RoleAssignment
from app.models.user import User

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login", auto_error=False)


ROLE_PERMISSIONS = {
    "super_admin": {"users.read", "users.write", "notaries.read", "notaries.write", "notaries.import", "crm.manage", "crm.audit.read", "cases.read", "cases.write"},
    "admin_notary": {"users.read", "users.write", "notaries.read", "notaries.write", "crm.manage", "crm.audit.read", "cases.read", "cases.write"},
    "notary": {"notaries.read", "crm.manage", "crm.audit.read", "cases.read", "cases.write"},
    "approver": {"notaries.read", "crm.manage", "cases.read", "cases.write"},
    "protocolist": {"notaries.read", "crm.manage", "cases.read", "cases.write"},
    "client": {"notaries.read", "cases.read"},
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raw_token = token or request.cookies.get("easypro2_session")
    if not raw_token:
        raise credentials_exception
    try:
        payload = jwt.decode(raw_token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    user = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .filter(User.id == user_id, User.is_active.is_(True))
        .first()
    )
    if user is None:
        raise credentials_exception
    return user


def get_role_codes(user: User) -> set[str]:
    return {assignment.role.code for assignment in user.role_assignments}


def get_manageable_notary_ids(user: User) -> set[int]:
    notary_ids = {assignment.notary_id for assignment in user.role_assignments if assignment.notary_id is not None}
    if user.default_notary_id is not None:
        notary_ids.add(user.default_notary_id)
    return notary_ids


def has_role(user: User, *role_codes: str, notary_id: int | None = None) -> bool:
    expected = set(role_codes)
    for assignment in user.role_assignments:
        if assignment.role.code not in expected:
            continue
        if assignment.notary_id is None or notary_id is None or assignment.notary_id == notary_id:
            return True
    return False


def get_permissions(user: User) -> list[str]:
    permissions: set[str] = set()
    for role_code in get_role_codes(user):
        permissions.update(ROLE_PERMISSIONS.get(role_code, set()))
    return sorted(permissions)


def require_roles(*role_codes: str) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if has_role(current_user, *role_codes):
            return current_user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para esta acción.")

    return dependency


def require_permission(permission: str) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if permission in get_permissions(current_user):
            return current_user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para esta acción.")

    return dependency
