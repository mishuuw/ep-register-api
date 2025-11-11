from sqlalchemy import TEXT, Column, BOOLEAN, ForeignKey
from src.models.base import BaseOrm

    
class RoleOrm(BaseOrm):
    title = Column(TEXT, default=None)
    description = Column(TEXT, default=None)
    
    ADMIN = Column(BOOLEAN, default=False)
    DIRECTOR = Column(BOOLEAN, default=False)
    MANAGER = Column(BOOLEAN, default=False)


class UserOrm(BaseOrm):
    role = Column(ForeignKey(RoleOrm.id), ondelete="CASCADE")