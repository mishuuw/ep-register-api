from sqlalchemy import (
    TEXT,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from src.models.base import BaseOrm
from src.models.enum import (
    EducationalFormEnum,
    EducationalProgramLanguageTypeEnum,
    EducationalstandardEnum,
    NetworkFormEnum,
)


class EducationalProgramActiveOrm(BaseOrm):
    __tablename__ = "educational_program_active"
    __table_args__ = (
        UniqueConstraint(
            "field_of_study_id",
            "start_year",
            "end_year",
            name="uq_field_of_study_start_end",
        ),
    )

    educational_program_id = Column(
        Integer, ForeignKey("educational_program.id"), nullable=False
    )
    field_of_study_id = Column(Integer, ForeignKey("field_of_study.id"), nullable=False)

    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)


class EducationalProgramOrm(BaseOrm):
    __tablename__ = "educational_program"

    title = Column(TEXT, nullable=False)
    title_short = Column(String(5))

    parent_id = Column(Integer, ForeignKey("educational_program.id"))
    school_id = Column(Integer, ForeignKey("school.id"))

    # accreditation_certificate_id = Column(Integer, ForeignKey("accreditation_certificate.id")) # noqa
    degree_id = Column(Integer, ForeignKey("degree.id"))
    partner_id = Column(Integer, ForeignKey("educational_program_partner.id"))

    network_form = Column(Enum(NetworkFormEnum))
    educational_form = Column(Enum(EducationalFormEnum))
    educational_standard_type = Column(Enum(EducationalstandardEnum))

    language = Column(Enum(EducationalProgramLanguageTypeEnum))
    language_hours = Column(Integer)

    curriculum_number = Column(TEXT)
    standard_duration_months = Column(Integer)
    poa_accreditation_expiry = Column(Date)
    state_accreditation_expiry = Column(Date)
    description = Column(TEXT)
