from typing import List, Optional, Union

from pydantic import BaseModel, Field, model_validator
from src.models.enum import TagTypeEnum

class TagSchema(BaseModel):
    name: str = Field(..., description="Tag name")
    type: TagTypeEnum = Field(..., description="Tag type: simple, boolean, number, text")

    boolean_value: Optional[bool] = Field(None, description="Boolean value")
    number_value: Optional[int] = Field(None, description="Number value")
    text_value: Optional[str] = Field(None, description="Text value")

    @model_validator(mode="after")
    def validate_value_by_type(self):
        if self.type == TagTypeEnum.SIMPLE:
            pass
        elif self.type == TagTypeEnum.BOOLEAN:
            if self.boolean_value is None:
                raise ValueError("boolean_value is required for boolean type")
        elif self.type == TagTypeEnum.NUMBER:
            if self.number_value is None:
                raise ValueError("number_value is required for number type")
        elif self.type == TagTypeEnum.TEXT:
            if self.text_value is None:
                raise ValueError("text_value is required for text type")
        return self

    def get_value(self) -> Union[str, bool, None]:
        if self.type == TagTypeEnum.BOOLEAN:
            return self.boolean_value
        elif self.type == TagTypeEnum.NUMBER:
            return self.number_value
        elif self.type == TagTypeEnum.TEXT:
            return self.text_value
        return None


class TagGetSchema(BaseModel):
    id: int = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")
    type: str = Field(..., description="Tag type: simple, boolean, number, text")
    value: Union[str, bool, None] = Field(None, description="Tag value based on type")


class TagUpdateSchema(BaseModel):
    id: int = Field(..., description="Tag ID")
    name: Optional[str] = Field(None, description="Tag name")
    type: Optional[str] = Field(None, description="Tag type: simple, boolean, number, text")
    boolean_value: Optional[bool] = Field(None, description="Boolean value")
    number_value: Optional[str] = Field(None, description="Number value")
    text_value: Optional[str] = Field(None, description="Text value")


class TagGetViewSchema(BaseModel):
    count: int = Field(..., description="Total count")
    result: List[TagGetSchema] = Field(..., description="List of Tags")


class TagToEducationalProgramSchema(BaseModel):
    tag_id: int = Field(..., description="Tag ID")
    educational_program_id: int = Field(..., description="Educational Program ID")
