"""
Data models and schemas for the FastAPI application using Pydantic.
Defines request payloads, response structures, and validation rules.
"""

from datetime import datetime, timezone
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
ALLOWED_ROLES = ["admin", "tester", "developer", "guest"]
ALLOWED_STATUSES = ["active", "inactive"]


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Full name of user")
    email: str = Field(..., description="Valid email address")
    role: str = Field(..., description="User role: admin, tester, developer, guest")
    status: str = Field(default="active", description="User status: active or inactive")
    age: int = Field(..., ge=18, le=100, description="Age must be between 18 and 100")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        value = value.strip()
        if not re.match(EMAIL_REGEX, value):
            raise ValueError(f"Invalid email format: '{value}'. Expected format: user@example.com")
        return value.lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ALLOWED_ROLES:
            raise ValueError(f"Invalid role: '{value}'. Allowed roles are: {', '.join(ALLOWED_ROLES)}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: '{value}'. Allowed statuses are: {', '.join(ALLOWED_STATUSES)}")
        return value


class UserCreate(UserBase):
    """Payload schema for creating a user (POST /users)."""
    pass


class UserUpdate(BaseModel):
    """Payload schema for full user update (PUT /users/{user_id})."""
    name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(...)
    role: str = Field(...)
    status: str = Field(...)
    age: int = Field(..., ge=18, le=100)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        value = value.strip()
        if not re.match(EMAIL_REGEX, value):
            raise ValueError(f"Invalid email format: '{value}'. Expected format: user@example.com")
        return value.lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ALLOWED_ROLES:
            raise ValueError(f"Invalid role: '{value}'. Allowed roles are: {', '.join(ALLOWED_ROLES)}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: '{value}'. Allowed statuses are: {', '.join(ALLOWED_STATUSES)}")
        return value


class UserPatch(BaseModel):
    """Payload schema for partial user update (PATCH /users/{user_id})."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=100)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not re.match(EMAIL_REGEX, value):
            raise ValueError(f"Invalid email format: '{value}'. Expected format: user@example.com")
        return value.lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().lower()
        if value not in ALLOWED_ROLES:
            raise ValueError(f"Invalid role: '{value}'. Allowed roles are: {', '.join(ALLOWED_ROLES)}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().lower()
        if value not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: '{value}'. Allowed statuses are: {', '.join(ALLOWED_STATUSES)}")
        return value


class UserResponse(BaseModel):
    """Standard user response schema."""
    id: int
    name: str
    email: str
    role: str
    status: str
    age: int
    created_at: str


class UserListResponse(BaseModel):
    """Paginated user list response schema."""
    total: int
    page: int
    limit: int
    data: List[UserResponse]


class LoginRequest(BaseModel):
    """Authentication login request payload."""
    username: str = Field(..., min_length=3, description="Username or email")
    password: str = Field(..., min_length=4, description="Password")


class TokenResponse(BaseModel):
    """Authentication successful response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    deleted_user_id: Optional[int] = None
