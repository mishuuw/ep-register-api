from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field
from src.models.enum import (
    EducationalFormEnum,
    EducationalProgramLanguageTypeEnum,
    EducationalStandartEnum,
    NetworkFormEnum,
)


# Общие схемы
class EducationalProgramSchema(BaseModel):
    title: str = Field(..., description="Title of the educational program")

    school_id: Optional[int] = Field(None, description="School id")
    degree_id: Optional[int] = Field(None, description="Degree id")
    partner_id: Optional[int] = Field(None, description="Partner id")

    # accreditation_certificate_id = Column(Integer,
    # ForeignKey("accreditation_certificate.id"))

    network_form: Optional[NetworkFormEnum] = Field(None, description="Network form")
    educational_form: Optional[EducationalFormEnum] = Field(
        None, description="Educational form"
    )
    educational_standart_type: Optional[EducationalStandartEnum] = Field(
        None, description="Educational standard type"
    )

    language: Optional[EducationalProgramLanguageTypeEnum] = Field(
        None, description="Language"
    )
    language_hours: Optional[int] = Field(None, description="Language hours")

    curriculum_number: Optional[str] = Field(None, description="Curriculum number")
    standard_duration_months: Optional[int] = Field(
        None, description="Standard duration in months"
    )
    poa_accreditation_expiry: Optional[date] = Field(
        None, description="POA accreditation expiry date"
    )
    state_accreditation_expiry: Optional[date] = Field(
        None, description="State accreditation expiry date"
    )
    description: Optional[str] = Field(None, description="Description")


class EducationalProgramGetSchema(EducationalProgramSchema):
    title: str = Field(..., description="Title of the educational program")

    school_title: Optional[str] = Field(None, description="School title")
    degree_title: Optional[str] = Field(None, description="Degree title")
    partner_title: Optional[str] = Field(None, description="Partner title")
    id: int = Field(..., description="Educational Program ID")
    network_form: Optional[NetworkFormEnum] = Field(None, description="Network form")
    educational_form: Optional[EducationalFormEnum] = Field(
        None, description="Educational form"
    )
    educational_standart_type: Optional[EducationalStandartEnum] = Field(
        None, description="Educational standard type"
    )

    language: Optional[EducationalProgramLanguageTypeEnum] = Field(
        None, description="Language"
    )
    language_hours: Optional[int] = Field(None, description="Language hours")

    curriculum_number: Optional[str] = Field(None, description="Curriculum number")
    standard_duration_months: Optional[int] = Field(
        None, description="Standard duration in months"
    )
    poa_accreditation_expiry: Optional[date] = Field(
        None, description="POA accreditation expiry date"
    )
    state_accreditation_expiry: Optional[date] = Field(
        None, description="State accreditation expiry date"
    )
    description: Optional[str] = Field(None, description="Description")


class EducationalProgramUpdateSchema(EducationalProgramSchema):
    title: Optional[str] = Field(None, description="Title of the educational program")
    is_active: Optional[bool] = Field(
        None, description="Is the educational program active"
    )


class EducationalProgramAddSchema(EducationalProgramSchema):
    is_active: bool = Field(..., description="Is the educational program active")


class EducationalProgramIdSchema(EducationalProgramSchema):
    id: int = Field(..., description="Educational Program ID")


class EducationalProgramGetFilterSchema(BaseModel):
    is_active: Optional[bool] = Field(None, description="Filter by active status")


class EducationalProgramGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramGetSchema] = Field(..., description="List of items")


# Схемы для активных ОП
class EducationalProgramActiveSchema(EducationalProgramGetSchema):
    field_of_study_id: int = Field(..., description="Field of Study ID")
    start_year: int = Field(..., description="Start year")
    end_year: int = Field(..., description="End year")


class EducationalProgramActiveViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramActiveSchema] = Field(
        ..., description="List of items"
    )


# Схемы для иерархии ОП
class EducationalProgramHierarchySchema(EducationalProgramIdSchema):
    parent: Optional[EducationalProgramHierarchySchema] = Field(
        None, description="Parent educational program"
    )
    children: Optional[List[EducationalProgramHierarchySchema]] = Field(
        default_factory=list, description="Child educational programs"
    )
    is_active: bool = Field(..., description="Is educational program active")
    field_of_study_id: Optional[int] = Field(None, description="Field of Study ID")
    start_year: Optional[int] = Field(None, description="Start year")
    end_year: Optional[int] = Field(None, description="End year")


class EducationalProgramHierarchyViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: EducationalProgramHierarchySchema = Field(
        ..., description="Hierarchy of educational programs"
    )
