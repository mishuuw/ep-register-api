from __future__ import annotations

from datetime import date
from typing import List, Optional, Literal

from pydantic import BaseModel, Field
from src.models.enum import (
    EducationalFormEnum,
    EducationalProgramLanguageTypeEnum,
    EducationalstandardEnum,
    NetworkFormEnum,
)


class EducationalProgramCoreFields(BaseModel):
    network_form: Optional[NetworkFormEnum] = Field(None, description="Network form")
    educational_form: Optional[EducationalFormEnum] = Field(
        None, description="Educational form"
    )
    educational_standard_type: Optional[EducationalstandardEnum] = Field(
        None, description="Educational standard type"
    )
    language: Optional[EducationalProgramLanguageTypeEnum] = Field(
        None, description="Language"
    )
    language_hours: Optional[int] = Field(None, description="Language hours")
    standard_duration_months: Optional[int] = Field(
        None, description="Standard duration in months"
    )
    poa_accreditation_company: Optional[str] = Field(
        None, description="POA accreditation company"
    )
    poa_accreditation_expiry: Optional[date] = Field(
        None, description="POA accreditation expiry date"
    )
    state_accreditation_expiry: Optional[date] = Field(
        None, description="State accreditation expiry date"
    )
    description: Optional[str] = Field(None, description="Description")


# Общие схемы
class EducationalProgramSchema(EducationalProgramCoreFields):
    title: str = Field(..., description="Title of the educational program")


class EducationalProgramGetSchema(EducationalProgramSchema):
    title_short: Optional[str] = Field(None, description="Short Title", max_length=5)
    school_title: Optional[str] = Field(None, description="School title")
    school_code: Optional[str] = Field(None, description="School code")
    degree_title: Optional[str] = Field(None, description="Degree title")
    partner_titles: Optional[List[str]] = Field(None, description="Partner titles")
    id: int = Field(..., description="Educational Program ID")


# NOTE: FIELD NAMES SHOULD ABSOLUTELY MATCH DB FIELD NAMING noqa
class EducationalProgramUpdateSchema(EducationalProgramCoreFields):
    title_short: Optional[str] = Field(None, description="Short Title", max_length=5)
    id: int = Field(..., description="Educational Program ID")
    title: Optional[str] = Field(None, description="Title of the educational program")
    is_active: Optional[bool] = Field(
        None, description="Is the educational program active"
    )
    field_of_study_id: Optional[int] = Field(
        None, description="Field of Study ID for filtering"
    )
    partner_ids: Optional[List[int]] = Field(
        default_factory=list, description="List of partner IDs"
    )
    start_year: Optional[int] = Field(None, description="Start year for filtering")
    end_year: Optional[int] = Field(None, description="End year for filtering")
    parent_id: Optional[int] = Field(None, description="Parent educational program ID")
    school_id: Optional[int] = Field(None, description="School ID")
    degree_id: Optional[int] = Field(None, description="Degree ID")


class EducationalProgramAddSchema(EducationalProgramSchema):
    parent_id: Optional[int] = Field(
        None,
        description="Parent educational program ID. If not None, unfilled fields will"
        " be inherited from parent.",
    )
    school_id: Optional[int] = Field(None, description="School ID")
    degree_id: Optional[int] = Field(None, description="Degree ID")
    title_short: Optional[str] = Field(None, description="Short Title")
    field_of_study_id: Optional[int] = Field(
        None, description="Field of Study ID for filtering"
    )
    partner_ids: Optional[List[int]] = Field(
        default_factory=list, description="List of partner IDs"
    )
    start_year: Optional[int] = Field(None, description="Start year for filtering")
    end_year: Optional[int] = Field(None, description="End year for filtering")
    is_active: Optional[bool] = Field(
        False, description="Is the educational program active"
    )


class EducationalProgramGetFilterSchema(BaseModel):
    mode: Optional[Literal["and", "or"]] = Field(
        "and",
        description="Режим фильтрации (AND/OR)"
    )

    network_form: Optional[NetworkFormEnum] = Field(None, description="Network form")
    educational_form: Optional[EducationalFormEnum] = Field(
        None, description="Educational form"
    )
    educational_standard_type: Optional[EducationalstandardEnum] = Field(
        None, description="Educational standard type"
    )
    language: Optional[EducationalProgramLanguageTypeEnum] = Field(
        None, description="Language"
    )
    language_hours: Optional[int] = Field(None, description="Language hours")
    standard_duration_months: Optional[int] = Field(
        None, description="Standard duration in months"
    )
    poa_accreditation_company: Optional[str] = Field(
        None, description="POA accreditation company"
    )
    poa_accreditation_expiry: Optional[date] = Field(
        None, description="POA accreditation expiry date"
    )
    poa_accreditation_expiry_is_null: Optional[bool] = Field(
        None, description="If true, filter programs that have no POA accreditation expiry"
    )
    state_accreditation_expiry: Optional[date] = Field(
        None, description="State accreditation expiry date"
    )
    state_accreditation_expiry_is_null: Optional[bool] = Field(
        None, description="If true, filter programs that have no state accreditation expiry"
    )
    title_contains: Optional[str] = Field(None, description="Partial search by title")
    school_id: Optional[int] = Field(None, description="School ID")
    degree_id: Optional[int] = Field(None, description="Degree ID")

class EducationalProgramGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramGetSchema] = Field(..., description="List of items")


# Схемы для активных ОП
class EducationalProgramActiveSchema(EducationalProgramGetSchema):
    field_of_study_title: str = Field(..., description="Field of Study Title")
    field_of_study_code: str = Field(..., description="Field of Study Code")
    start_year: int = Field(..., description="Start year")
    end_year: int = Field(..., description="End year")

class EducationalProgramActiveGetFilterSchema(EducationalProgramGetFilterSchema):
    field_of_study_id: Optional[int] = Field(
        None, description="Field of Study ID for filtering"
    )
    start_year: Optional[int] = Field(None, description="Start year for filtering")
    end_year: Optional[int] = Field(None, description="End year for filtering")

class EducationalProgramActiveViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramActiveSchema] = Field(
        ..., description="List of items"
    )


# Схемы для иерархии ОП
class EducationalProgramHierarchySchema(EducationalProgramGetSchema):
    parent_id: Optional[int] = Field(None, description="Parent educational program ID")
    parent: Optional[EducationalProgramHierarchySchema] = Field(
        None, description="Parent educational program"
    )
    children: List[EducationalProgramHierarchySchema] = Field(
        default_factory=list, description="Child educational programs"
    )
    is_active: bool = Field(..., description="Is educational program active")
    field_of_study_title: Optional[str] = Field(..., description="Field of Study Title")
    field_of_study_code: Optional[str] = Field(..., description="Field of Study Code")
    start_year: Optional[int] = Field(None, description="Start year")
    end_year: Optional[int] = Field(None, description="End year")


class EducationalProgramHierarchyViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramHierarchySchema] = Field(
        ..., description="Hierarchy of educational programs"
    )
