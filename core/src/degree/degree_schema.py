from typing import List,Optional

from pydantic import BaseModel, Field



class DegreeFilterSchema(BaseModel):
    id: int = Field(..., description="some ID")
    
class DegreeGetSchema(BaseModel):
    id: int = Field(..., description="some ID")

class DegreeAddSchema(BaseModel):
    id: int = Field(..., description="some ID")
    
class DegreeGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[DegreeGetSchema] = Field(..., description="List of items")
