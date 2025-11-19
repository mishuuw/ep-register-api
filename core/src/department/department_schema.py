from typing import List, Optional

from pydantic import BaseModel, Field


class DepartmentSchema(BaseModel):
    code: str = Field(..., description="Department code", max_length=10)
    title: str = Field(..., description="Department title")
    title_short: str = Field(..., description="Short department title", max_length=20)
    school_id: int = Field(..., description="School ID")


class DepartmentGetSchema(DepartmentSchema):
    id: int = Field(..., description="Department ID")


class DepartmentAddSchema(DepartmentSchema):
    pass


class DepartmentUpdateSchema(BaseModel):
    id: int = Field(..., description="Department ID")
    code: Optional[str] = Field(None, description="Department code", max_length=10)
    title: Optional[str] = Field(None, description="Department title")
    title_short: Optional[str] = Field(None, description="Short department title", max_length=20)
    school_id: Optional[int] = Field(None, description="School ID")


class DepartmentFilterSchema(BaseModel):
    school_id: Optional[int] = Field(None, description="School ID filter")


class DepartmentGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[DepartmentGetSchema] = Field(..., description="List of departments")