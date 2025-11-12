from typing import List,Optional

from pydantic import BaseModel, Field



class EducationalProgramFilterSchema(BaseModel):
    id: int = Field(..., description="some ID")
    
class EducationalProgramGetSchema(BaseModel):
    id: int = Field(..., description="some ID")

class EducationalProgramAddSchema(BaseModel):
    id: int = Field(..., description="some ID")
    
class EducationalProgramGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramGetSchema] = Field(..., description="List of items")