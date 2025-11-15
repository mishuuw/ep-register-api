from sqlalchemy import (
    TEXT,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
)
from src.models.base import BaseOrm
from src.models.enum import (
    EducationalFormEnum,
    EducationalProgramLanguageTypeEnum,
    EducationalStandartEnum,
    NetworkFormEnum,
)


class EducationalProgramActiveOrm(BaseOrm):
    __tablename__ = "educational_program_active"

    educational_program_id = Column(
        Integer, ForeignKey("educational_program.id"), unique=True, nullable=False
    )
    field_of_study_id = Column(Integer, ForeignKey("field_of_study.id"), nullable=False)

    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)


class EducationalProgramOrm(BaseOrm):
    __tablename__ = "educational_program"

    title = Column(TEXT, nullable=False)

    parent_id = Column(Integer, ForeignKey("educational_program.id"))
    school_id = Column(Integer, ForeignKey("school.id"))

    # accreditation_certificate_id = Column(Integer, ForeignKey("accreditation_certificate.id")) # noqa
    degree_id = Column(Integer, ForeignKey("degree.id"))
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
