from sqlalchemy import TEXT, Column
from src.models.base import BaseOrm


class DegreeOrm(BaseOrm):
    __tablename__ = "degree"
    title = Column(TEXT, nullable=False)
