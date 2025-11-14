from typing import List,Optional

from pydantic import BaseModel, Field



class SchoolSchema(BaseModel):
    code: str = Field(..., description="School code", max_length=3)
    title: str = Field(..., description="School title")
    title_short: str = Field(..., description="Short school title", max_length=20)

class SchoolGetSchema(SchoolSchema):
    id: int = Field(..., description="School ID")

class SchoolUpdateSchema(BaseModel):
    id: int = Field(..., description="School ID")
    code: Optional[str] = Field(None, description="School code", max_length=3)
    title: Optional[str] = Field(None, description="School title")
    title_short: Optional[str] = Field(None, description="Short school title", max_length=20)

class SchoolGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[SchoolGetSchema] = Field(..., description="List of schools")
