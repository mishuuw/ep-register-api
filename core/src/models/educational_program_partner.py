from sqlalchemy import TEXT, Column, Enum, Integer
from src.models.base import BaseOrm
from src.models.enum import EducationalProgramPartnerEnum


class EducationalProgramPartnerOrm(BaseOrm):
    __tablename__ = "educational_program_partner"

    title = Column(TEXT, nullable=False)
    partner_type = Column(Enum(EducationalProgramPartnerEnum), nullable=False)
    hours = Column(Integer)
