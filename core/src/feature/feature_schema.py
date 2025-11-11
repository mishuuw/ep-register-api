from typing import List,Optional

from pydantic import BaseModel, Field



class FeatureGetSchema(BaseModel):
    id: int = Field(..., description="some ID")

class FeatureAddSchema(BaseModel):
    id: int = Field(..., description="some ID")

    some_info: Optional[List[str]] = Field(...)
    
class FeatureGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[FeatureGetSchema] = Field(..., description="List of items")
    
class FeatureAddViewSchema(BaseModel):
    id: int = Field(..., description="some ID")