from datetime import timedelta

from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.deps import get_permissions, get_role_codes
from app.core.security import create_access_token, verify_password
from app.models.role_assignment import RoleAssignment
from app.models.user import User
from app.schemas.user import UserRoleAssignmentSummary


class AuthenticationError(Exception):
    pass


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .filter(User.email == email)
        .first()
    )
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise AuthenticationError("Credenciales inválidas.")
    return user


def serialize_assignments(user: User) -> list[UserRoleAssignmentSummary]:
    return [
        UserRoleAssignmentSummary(
            id=assignment.id,
            role_id=assignment.role_id,
            role_code=assignment.role.code,
            role_name=assignment.role.name,
            notary_id=assignment.notary_id,
            notary_label=assignment.notary.notary_label if assignment.notary else None,
        )
        for assignment in sorted(
            user.role_assignments,
            key=lambda item: (item.role.name, item.notary.notary_label if item.notary else ""),
        )
    ]


def serialize_user(user: User) -> dict:
    assignment_labels = []
    for assignment in user.role_assignments:
        suffix = f"@{assignment.notary.slug}" if assignment.notary else "@global"
        assignment_labels.append(f"{assignment.role.code}{suffix}")

    role_codes = sorted(get_role_codes(user))
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": assignment_labels,
        "role_codes": role_codes,
        "permissions": get_permissions(user),
        "default_notary": user.default_notary.notary_label if user.default_notary else None,
        "assignments": serialize_assignments(user),
    }


def build_login_response(user: User) -> dict:
    settings = get_settings()
    claims = {
        "email": user.email,
        "roles": sorted(get_role_codes(user)),
        "notary_id": user.default_notary_id,
        "permissions": get_permissions(user),
    }
    token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims=claims,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }
