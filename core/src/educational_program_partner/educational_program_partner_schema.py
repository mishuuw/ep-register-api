from typing import List

from pydantic import BaseModel, Field


class EducationalProgramPartnerFilterSchema(BaseModel):
    id: int = Field(..., description="some ID")


class EducationalProgramPartnerGetSchema(BaseModel):
    id: int = Field(..., description="some ID")


class EducationalProgramPartnerAddSchema(BaseModel):
    id: int = Field(..., description="some ID")


class EducationalProgramPartnerGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramPartnerGetSchema] = Field(
        ..., description="List of items"
    )
