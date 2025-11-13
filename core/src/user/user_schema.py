from typing import  Optional
from pydantic import BaseModel, EmailStr, Field
from src.models.enum import AccessLevelEnum
    
class RoleSchema(BaseModel):
    title: str = Field(None, description="Role title")
    access_level: AccessLevelEnum = Field(..., description="Access level")
    school_id: Optional[int] = Field(..., description="School ID")


class UserSchema(BaseModel):
    email: EmailStr = Field(..., description="User email")
    phone: str = Field(..., description="User phone number")
    position: str = Field(..., description="User position")
    full_name: str = Field(..., description="User full name")
    internal_number: str = Field(..., description="User internal number")
    
    role_id: int = Field(None, description="Role ID")
    department_id: int = Field(None, description="Department ID")
    
    is_active: bool = Field(True, description="Is active")