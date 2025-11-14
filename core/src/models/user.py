from sqlalchemy import TEXT, Column, BOOLEAN, Enum, ForeignKey, CheckConstraint, CHAR
from src.models.base import BaseOrm
from src.models.enum import AccessLevelEnum

class UserOrm(BaseOrm):
    __tablename__ = "user"
    
    email = Column(TEXT)
    phone = Column(TEXT)
    position = Column(TEXT)
    full_name = Column(TEXT)
    internal_number = Column(TEXT)
    
    access_level = Column(Enum(AccessLevelEnum), nullable=True)
    school_id = Column(ForeignKey("school.id", ondelete="SET NULL"))
    field_of_study_id = Column(ForeignKey("field_of_study.id", ondelete="SET NULL"))
    department_id = Column(ForeignKey("department.id", ondelete="SET NULL"))
    
    is_active = Column(BOOLEAN, nullable=False, default=True)