from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRoleAssignmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    role_code: str
    role_name: str
    notary_id: int | None = None
    notary_label: str | None = None


class RoleCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    scope: str
    description: str


class RoleCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=80)
    scope: str = Field(min_length=2, max_length=30)
    description: str = Field(default="", max_length=255)


class RoleUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(default="", max_length=255)


class RolePermissionItem(BaseModel):
    module_code: str = Field(min_length=1, max_length=80)
    can_access: bool


class UserRoleAssignmentInput(BaseModel):
    role_code: str = Field(min_length=2, max_length=50)
    notary_id: int | None = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    is_active: bool = True
    phone: str | None = Field(default=None, max_length=40)
    job_title: str | None = Field(default=None, max_length=80)
    default_notary_id: int | None = None
    assignments: list[UserRoleAssignmentInput] = []


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=120)


class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=120)


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    phone: str | None = None
    job_title: str | None = None
    default_notary_id: int | None = None
    default_notary_label: str | None = None
    roles: list[str]
    assignments: list[UserRoleAssignmentSummary]


class UserDetail(UserSummary):
    pass


class UserOption(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    default_notary_id: int | None = None
    default_notary_label: str | None = None


class UserStatusUpdate(BaseModel):
    is_active: bool
