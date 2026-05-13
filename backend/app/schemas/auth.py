from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.user import UserRoleAssignmentSummary


class AuthenticatedUser(BaseModel):
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
    permissions: list[str]
    default_notary: str | None = None
    assignments: list[UserRoleAssignmentSummary] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CurrentUserProfileUpdate(BaseModel):
    full_name: str
    phone: str | None = None
    job_title: str | None = None
    password: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser
