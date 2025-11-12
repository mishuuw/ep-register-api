from sqlalchemy import TEXT, Column, BOOLEAN, Enum, ForeignKey, CheckConstraint, CHAR, Integer, String, Date
from src.models.base import BaseOrm
from src.models.enum import (
    EducationalProgramPartnerEnum,
    NetworkFormEnum,
    EducationalFormEnum,
    EducationalStandartEnum,
    EducationalProgramLanguageTypeEnum,
)

class EducationalProgramActiveOrm(BaseOrm):
    __tablename__ = "educational_program_active"

    educational_program_id = Column(Integer, ForeignKey("educational_program.id"))
    start_year = Column(Integer)
    end_year = Column(Integer)

class EducationalProgramOrm(BaseOrm):
    __tablename__ = "educational_program"

    title = Column(TEXT, nullable=False)

    parent_id = Column(Integer, ForeignKey("educational_program.id"))
    school_code = Column(String(3), ForeignKey("school.code"))
    field_of_study_code = Column(String(8), ForeignKey("field_of_study.code"))
    #accreditation_certificate_id = Column(Integer, ForeignKey("accreditation_certificate.id"))
    degree_id = Column(Integer, ForeignKey("degree.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("educational_program_partner.id"))

    network_form = Column(Enum(NetworkFormEnum))
    educational_form = Column(Enum(EducationalFormEnum))
    educational_standart_type = Column(Enum(EducationalStandartEnum))
    
    language = Column(Enum(EducationalProgramLanguageTypeEnum))
    language_hours = Column(Integer)

    curriculum_number = Column(TEXT)
    standart_duration_months = Column(Integer)
    poa_accreditation_expiry = Column(Date)
    state_accreditation_expiry = Column(Date)
    description = Column(TEXT)

 