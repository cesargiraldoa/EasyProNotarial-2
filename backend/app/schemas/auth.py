from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.user import UserRoleAssignmentSummary


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    roles: list[str]
    role_codes: list[str]
    permissions: list[str]
    default_notary: str | None = None
    assignments: list[UserRoleAssignmentSummary] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser
