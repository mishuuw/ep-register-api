from typing import List

from pydantic import BaseModel, Field


class DepartmentFilterSchema(BaseModel):
    id: int = Field(..., description="some ID")


class DepartmentGetSchema(BaseModel):
    id: int = Field(..., description="some ID")


class DepartmentAddSchema(BaseModel):
    id: int = Field(..., description="some ID")


class DepartmentGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[DepartmentGetSchema] = Field(..., description="List of items")
