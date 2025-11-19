from typing import List, Optional

from pydantic import BaseModel, Field


class EducationalProgramPartnerSchema(BaseModel):
    educational_program_id: int = Field(..., description="Educational Program ID")
    partner_name: str = Field(..., description="Partner name")
    partner_type: str = Field(..., description="Partner type")
    contact_person: Optional[str] = Field(None, description="Contact person")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")


class EducationalProgramPartnerGetSchema(EducationalProgramPartnerSchema):
    id: int = Field(..., description="Educational Program Partner ID")


class EducationalProgramPartnerAddSchema(EducationalProgramPartnerSchema):
    pass


class EducationalProgramPartnerUpdateSchema(BaseModel):
    id: int = Field(..., description="Educational Program Partner ID")
    educational_program_id: Optional[int] = Field(None, description="Educational Program ID")
    partner_name: Optional[str] = Field(None, description="Partner name")
    partner_type: Optional[str] = Field(None, description="Partner type")
    contact_person: Optional[str] = Field(None, description="Contact person")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")


class EducationalProgramPartnerFilterSchema(BaseModel):
    educational_program_id: Optional[int] = Field(None, description="Filter by educational program ID")
    partner_type: Optional[str] = Field(None, description="Filter by partner type")


class EducationalProgramPartnerGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramPartnerGetSchema] = Field(
        ..., description="List of educational program partners"
    )