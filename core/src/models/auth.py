from sqlalchemy import TEXT, Column, ForeignKey, Integer, Boolean, DateTime
from src.models.base import BaseOrm


class AuthOrm(BaseOrm):
    __tablename__ = "auth"
    token_hash = Column(
        TEXT,
        nullable=False,
        unique=True,
        index=True,
        comment="Opaque token",
    )
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)


class CredentialsOrm(BaseOrm):
    __tablename__ = "credentials"
    password_hash = Column(TEXT, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
