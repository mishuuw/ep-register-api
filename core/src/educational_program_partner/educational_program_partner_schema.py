from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.enum import EducationalProgramPartnerEnum


class EducationalProgramPartnerSchema(BaseModel):
    title: str = Field(..., description="Title of the educational program partner")
    partner_type: EducationalProgramPartnerEnum = Field(
        ..., description="Type of the partner"
    )
    hours: Optional[int] = Field(None, description="Number of hours")


class EducationalProgramPartnerGetSchema(EducationalProgramPartnerSchema):
    id: int = Field(..., description="Educational Program Partner ID")


class EducationalProgramPartnerUpdateSchema(BaseModel):
    id: int = Field(..., description="Educational Program Partner ID")
    title: Optional[str] = Field(
        None, description="Title of the educational program partner"
    )
    partner_type: Optional[EducationalProgramPartnerEnum] = Field(
        None, description="Type of the partner"
    )
    hours: Optional[int] = Field(None, description="Number of hours")


class EducationalProgramPartnerFilterSchema(BaseModel):
    partner_type: Optional[EducationalProgramPartnerEnum] = Field(
        None, description="Filter by partner type"
    )


class EducationalProgramPartnerGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramPartnerGetSchema] = Field(
        ..., description="List of educational program partners"
    )
