from sqlalchemy import TEXT, Column
from src.models.base import BaseOrm


class DepartmentOrm(BaseOrm):
    __tablename__ = "department"
    title = Column(TEXT, default=None)
