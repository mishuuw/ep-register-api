from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from src.models.enum import AccessLevelEnum


class UserSchema(BaseModel):
    email: Optional[EmailStr] = Field(..., description="User email")
    phone: Optional[str] = Field(..., description="User phone number")
    position: Optional[str] = Field(..., description="User position")
    full_name: Optional[str] = Field(..., description="User full name")
    internal_number: Optional[str] = Field(..., description="User internal number")

    access_level: Optional[AccessLevelEnum] = Field(None, description="Access level")
    field_of_study_id: Optional[int] = Field(None, description="Field of Study ID")
    school_id: Optional[int] = Field(None, description="School ID", le=3)
    department_id: Optional[int] = Field(None, description="Department ID")

    is_active: bool = Field(True, description="Is active")


class UserGetSchema(BaseModel):
    id: int = Field(..., description="User ID")
    email: Optional[EmailStr] = Field(..., description="User email")
    phone: Optional[str] = Field(..., description="User phone number")
    position: Optional[str] = Field(..., description="User position")
    full_name: Optional[str] = Field(..., description="User full name")
    internal_number: Optional[str] = Field(..., description="User internal number")

    access_level: Optional[AccessLevelEnum] = Field(None, description="Access level")
    field_of_study: Optional[str] = Field(
        None,
        description="Field of Study code",
        pattern="^[0-9]{2}\.[0-9]{2}\.[0-9]{2}[A-Za-z\u0400-\u04ff]*$",  # noqa
    )
    school_title: Optional[str] = Field(None, description="School title")
    department_title: Optional[str] = Field(None, description="Department title")

    is_active: bool = Field(True, description="Is active")


class UserGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: list[UserGetSchema] = Field(..., description="List of users")


class UserUpdateSchema(BaseModel):
    id: int = Field(..., description="User ID")
    email: Optional[EmailStr] = Field(None, description="User email")
    phone: Optional[str] = Field(None, description="User phone number")
    position: Optional[str] = Field(None, description="User position")
    full_name: Optional[str] = Field(None, description="User full name")
    internal_number: Optional[str] = Field(None, description="User internal number")

    access_level: Optional[AccessLevelEnum] = Field(None, description="Access level")
    field_of_study_id: Optional[int] = Field(None, description="Field of Study ID")
    school_id: Optional[int] = Field(None, description="School ID", le=3)
    department_id: Optional[int] = Field(None, description="Department ID")

    is_active: Optional[bool] = Field(..., description="Is active")
