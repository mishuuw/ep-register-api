from typing import List, Optional

from pydantic import BaseModel, Field


class DepartmentSchema(BaseModel):
    title: str = Field(..., description="Department title")


class DepartmentGetSchema(DepartmentSchema):
    id: int = Field(..., description="Department ID")


class DepartmentAddSchema(DepartmentSchema):
    pass


class DepartmentUpdateSchema(BaseModel):
    id: int = Field(..., description="Department ID")
    title: Optional[str] = Field(None, description="Department title")


class DepartmentGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[DepartmentGetSchema] = Field(..., description="List of departments")
