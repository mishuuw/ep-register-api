from typing import List, Optional

from pydantic import BaseModel, Field


class FieldOfStudySchema(BaseModel):
    code: str = Field(
        ...,
        pattern=r"^[0-9]{2}\.[0-9]{2}\.[0-9]{2}$",
        description="Field of Study code",
    )
    title: str = Field(..., description="Field of Study title")
    title_short: str = Field(
        ..., description="Field of Study short title", max_length=5
    )


class FieldOfStudyGetSchema(FieldOfStudySchema):
    id: int = Field(..., description="Field of Study ID")


class FieldOfStudyUpdateSchema(BaseModel):
    id: int = Field(..., description="Field of Study ID")
    code: Optional[str] = Field(
        None,
        pattern=r"^[0-9]{2}\.[0-9]{2}\.[0-9]{2}$",
        description="Field of Study code",
    )
    title: Optional[str] = Field(None, description="Field of Study title")
    title_short: Optional[str] = Field(
        None, description="Field of Study short title", max_length=5
    )


class FieldOfStudyGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[FieldOfStudyGetSchema] = Field(
        ..., description="List of Fields of Study"
    )

