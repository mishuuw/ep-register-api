from typing import List,Optional

from pydantic import BaseModel, Field



class DegreeGetSchema(BaseModel):
    id: int = Field(..., description="Degree ID")
    title: str = Field(..., description="Degree title")

class DegreeAddSchema(BaseModel):
    title: str = Field(..., description="Degree title")

class DegreeUpdateSchema(BaseModel):
    id: int = Field(..., description="Degree ID")
    title: Optional[str] = Field(None, description="new degree title")

class DegreeGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[DegreeGetSchema] = Field(..., description="List of items")
