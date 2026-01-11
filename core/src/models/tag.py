from sqlalchemy import TEXT, Enum, Column, String, BOOLEAN, Integer, ForeignKey, UniqueConstraint
from src.models.base import BaseOrm
from src.models.enum import TagTypeEnum

class TagOrm(BaseOrm):
    __tablename__ = "tag"

    name = Column(TEXT, nullable=False)
    type = Column(Enum(TagTypeEnum), nullable=False)
    
    boolean_value = Column(BOOLEAN, nullable=True)
    number_value = Column(Integer, nullable=True)
    text_value = Column(TEXT, nullable=True)

    def get_value(self):
        if self.type == TagTypeEnum.BOOLEAN:
            return self.boolean_value
        elif self.type == TagTypeEnum.NUMBER:
            return self.number_value
        elif self.type == TagTypeEnum.TEXT:
            return self.text_value
        return None


class TagToEducationalProgramOrm(BaseOrm):
    __tablename__ = "tag_to_educational_program"
    __table_args__ = (
        UniqueConstraint(
            "educational_program_id",
            "tag_id",
            name="uq_educational_program_tag",
        ),
    )

    tag_id = Column(
        Integer,
        ForeignKey("tag.id", ondelete="CASCADE"),
        nullable=False,
    )
    educational_program_id = Column(
        Integer,
        ForeignKey("educational_program.id", ondelete="CASCADE"),
        nullable=False,
    )
