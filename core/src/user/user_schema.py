from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
    
class RoleSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    ADMIN: Optional[bool] = False
    DIRECTOR: Optional[bool] = False
    MANAGER: Optional[bool] = False


class UserSchema(BaseModel):
    id: int
    role: List[RoleSchema] | None = []