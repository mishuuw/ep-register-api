from typing import List,Optional

from pydantic import BaseModel, Field



class FieldOfStudyFilterSchema(BaseModel):
    id: int = Field(..., description="some ID")
    
class FieldOfStudyGetSchema(BaseModel):
    id: int = Field(..., description="some ID")

class FieldOfStudyAddSchema(BaseModel):
    id: int = Field(..., description="some ID")
    
class FieldOfStudyGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[FieldOfStudyGetSchema] = Field(..., description="List of items")
