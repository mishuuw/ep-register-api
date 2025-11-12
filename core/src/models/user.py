from sqlalchemy import TEXT, Column, BOOLEAN, Enum, ForeignKey, CheckConstraint, CHAR
from src.models.base import BaseOrm
from src.models.enum import AccessLevelEnum

    
class RoleOrm(BaseOrm):
    __tablename__ = "role"
    
    title = Column(TEXT, default=None)
    access_level = Column(Enum(AccessLevelEnum), nullable=False)
    
    school_id = Column(ForeignKey("school.id"))


class UserOrm(BaseOrm):
    __tablename__ = "user"
    
    email = Column(TEXT)
    phone = Column(TEXT)
    position = Column(TEXT)
    full_name = Column(TEXT)
    internal_number = Column(TEXT)
    
    role_id = Column(ForeignKey("role.id", ondelete="SET NULL"))
    department_id = Column(ForeignKey("department.id", ondelete="SET NULL"))
    
    is_active = Column(BOOLEAN, nullable=False, default=True)