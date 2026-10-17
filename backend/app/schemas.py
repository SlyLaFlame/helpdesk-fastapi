from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .models import Category, Priority, Role, Status


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- Users ----
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    department: str = ""
    role: Role = Role.student  # only student/staff honoured on self-registration

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        # bcrypt only uses the first 72 bytes and newer versions raise an
        # error beyond that, which would otherwise surface as a 500.
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return v


class UserOut(ORM):
    id: int
    name: str
    email: EmailStr
    role: Role
    department: str


class UserBrief(ORM):
    id: int
    name: str


class RoleUpdate(BaseModel):
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---- Tickets ----
class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    category: Category = Category.other
    priority: Priority = Priority.medium


class TicketUpdate(BaseModel):
    status: Status | None = None
    priority: Priority | None = None
    assigned_to: int | None = None
    unassign: bool = False


class CommentCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=3000)


class CommentOut(ORM):
    id: int
    comment: str
    is_system: bool
    created_at: datetime
    author: UserBrief


class TicketOut(ORM):
    id: int
    title: str
    description: str
    category: Category
    status: Status
    priority: Priority
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    creator: UserBrief
    assignee: UserBrief | None


class TicketDetail(TicketOut):
    comments: list[CommentOut]


# ---- Analytics ----
class CountItem(BaseModel):
    label: str
    count: int


class Analytics(BaseModel):
    total: int
    open_count: int
    closed_count: int
    avg_resolution_hours: float | None
    by_category: list[CountItem]
    by_status: list[CountItem]