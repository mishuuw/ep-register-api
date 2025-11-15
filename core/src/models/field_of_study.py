from sqlalchemy import TEXT, CheckConstraint, Column, String
from src.models.base import BaseOrm


class FieldOfStudyOrm(BaseOrm):
    __tablename__ = "field_of_study"

    code = Column(String(8), nullable=False, unique=True, comment="Format: XX.XX.XX")

    title = Column(TEXT, nullable=False)
    title_short = Column(
        String(5),
        nullable=False,
        comment="Format: XX.XX.XXTTTTT, ex. 09.03.03ру; 'ру' = title_short",
    )

    __table_args__ = (
        CheckConstraint(
            "code ~ '^[0-9]{2}\\.[0-9]{2}\\.[0-9]{2}$'",
            name="ck_field_of_study_code_format",
        ),
    )
