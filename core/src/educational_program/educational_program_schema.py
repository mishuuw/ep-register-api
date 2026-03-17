from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

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
    tags: Optional[dict[str, dict]] = Field(default_factory=dict, description="Tags")
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
    class FilterLogicEnum(str, Enum):
        AND = "AND"
        OR = "OR"

    field_of_study_id: Optional[int] = Field(
        None, description="Field of Study ID for filtering"
    )
    start_year: Optional[int] = Field(None, description="Start year for filtering")
    end_year: Optional[int] = Field(None, description="End year for filtering")
    include_tag_ids: Optional[List[int]] = Field(
        default_factory=list,
        description="Tag IDs to include (programs must have these tags)"
    )
    exclude_tag_ids: Optional[List[int]] = Field(
        default_factory=list,
        description="Tag IDs to exclude (programs must NOT have these tags)"
    )
    include_logic: FilterLogicEnum = Field(
        default=FilterLogicEnum.AND,
        description="Logic for include tags: AND (must have all) or OR (must have at least one)"
    )
    exclude_logic: FilterLogicEnum = Field(
        default=FilterLogicEnum.OR,
        description="Logic for exclude tags: AND (must not have all) or OR (must not have any)"
    )


class EducationalProgramGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramGetSchema] = Field(..., description="List of items")


# Схемы для активных ОП
class EducationalProgramActiveSchema(EducationalProgramGetSchema):
    field_of_study_title: str = Field(..., description="Field of Study Title")
    field_of_study_code: str = Field(..., description="Field of Study Code")
    start_year: int = Field(..., description="Start year")
    end_year: int = Field(..., description="End year")


class EducationalProgramActiveViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[EducationalProgramActiveSchema] = Field(
        ..., description="List of items"
    )


class SortOrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"


class EducationalProgramActiveSortByEnum(str, Enum):
    id = "id"
    title = "title"
    title_short = "title_short"
    degree_title = "degree_title"
    school_title = "school_title"
    school_code = "school_code"
    partner_titles = "partner_titles"
    field_of_study_title = "field_of_study_title"
    field_of_study_code = "field_of_study_code"
    start_year = "start_year"
    end_year = "end_year"
    network_form = "network_form"
    educational_form = "educational_form"
    educational_standard_type = "educational_standard_type"
    language = "language"
    language_hours = "language_hours"
    standard_duration_months = "standard_duration_months"
    poa_accreditation_company = "poa_accreditation_company"
    poa_accreditation_expiry = "poa_accreditation_expiry"
    state_accreditation_expiry = "state_accreditation_expiry"
    description = "description"


class EducationalProgramActiveExportFilterSchema(BaseModel):
    id_in: Optional[List[int]] = Field(default_factory=list)
    title_in: Optional[List[str]] = Field(default_factory=list)
    title_short_in: Optional[List[str]] = Field(default_factory=list)
    degree_title_in: Optional[List[str]] = Field(default_factory=list)
    school_title_in: Optional[List[str]] = Field(default_factory=list)
    school_code_in: Optional[List[str]] = Field(default_factory=list)
    partner_title_in: Optional[List[str]] = Field(default_factory=list)
    field_of_study_title_in: Optional[List[str]] = Field(default_factory=list)
    field_of_study_code_in: Optional[List[str]] = Field(default_factory=list)
    start_year_in: Optional[List[int]] = Field(default_factory=list)
    end_year_in: Optional[List[int]] = Field(default_factory=list)
    network_form_in: Optional[List[NetworkFormEnum]] = Field(default_factory=list)
    educational_form_in: Optional[List[EducationalFormEnum]] = Field(
        default_factory=list
    )
    educational_standard_type_in: Optional[List[EducationalstandardEnum]] = Field(
        default_factory=list
    )
    language_in: Optional[List[EducationalProgramLanguageTypeEnum]] = Field(
        default_factory=list
    )
    language_hours_in: Optional[List[int]] = Field(default_factory=list)
    standard_duration_months_in: Optional[List[int]] = Field(default_factory=list)
    poa_accreditation_company_in: Optional[List[str]] = Field(default_factory=list)
    poa_accreditation_expiry_from: Optional[date] = None
    poa_accreditation_expiry_to: Optional[date] = None
    state_accreditation_expiry_from: Optional[date] = None
    state_accreditation_expiry_to: Optional[date] = None
    description_contains: Optional[str] = None
    search: Optional[str] = None


class EducationalProgramActiveExportRequestSchema(BaseModel):
    base_filter: EducationalProgramGetFilterSchema = Field(
        default_factory=EducationalProgramGetFilterSchema
    )
    filter_by: EducationalProgramActiveExportFilterSchema = Field(
        default_factory=EducationalProgramActiveExportFilterSchema
    )
    sort_by: EducationalProgramActiveSortByEnum = Field(
        default=EducationalProgramActiveSortByEnum.title
    )
    sort_order: SortOrderEnum = Field(default=SortOrderEnum.ASC)


# Схемы для иерархии ОП
class EducationalProgramHierarchySchema(EducationalProgramGetSchema):
    parent_id: Optional[int] = Field(None, description="Parent educational program ID")
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
