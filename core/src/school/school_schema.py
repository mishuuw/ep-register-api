from typing import List,Optional

from pydantic import BaseModel, Field



class SchoolFilterSchema(BaseModel):
    id: int = Field(..., description="some ID")
    
class SchoolGetSchema(BaseModel):
    id: int = Field(..., description="some ID")

class SchoolAddSchema(BaseModel):
    id: int = Field(..., description="some ID")
    
class SchoolGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[SchoolGetSchema] = Field(..., description="List of items")
