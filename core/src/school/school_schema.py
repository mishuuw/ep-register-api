from typing import List,Optional

from pydantic import BaseModel, Field



class SchoolSchema(BaseModel):
    code: str = Field(..., description="School code")
    title: str = Field(..., description="School title")
    title_short: str = Field(..., description="Short school title")

class SchoolGetSchema(SchoolSchema):
    id: int = Field(..., description="School ID")

class SchoolUpdateSchema(BaseModel):
    id: int = Field(..., description="School ID")
    code: Optional[str] = Field(None, description="School code")
    title: Optional[str] = Field(None, description="School title")
    title_short: Optional[str] = Field(None, description="Short school title")

class SchoolGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[SchoolGetSchema] = Field(..., description="List of schools")
