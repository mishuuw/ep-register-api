from sqlalchemy import TEXT, Column, String
from src.models.base import BaseOrm


class SchoolOrm(BaseOrm):
    __tablename__ = "school"

    code = Column(String(3), nullable=False, unique=True)

    title = Column(TEXT, nullable=False)
    title_short = Column(String(20))
