from typing import Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessSchema(BaseModel):
    detail: str


class ErrorSchema(BaseModel):
    code: str
    detail: str

class DependencyCheckSchema:
    def __init__(
        self,
        table: T,
        id: int,
    ):
        self.table = table
        self.id = id