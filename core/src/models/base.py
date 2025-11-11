from datetime import datetime, timezone
from typing import Any, Awaitable, TypeVar

import sqlalchemy as sa
from sqlalchemy import BigInteger, Column, DateTime, MetaData
from sqlalchemy.orm import Mapped, declarative_base
from sqlalchemy.util import greenlet_spawn

"""
alembic requires constraints to be named.
This sets up a naming convention rather than manually naming
https://alembic.sqlalchemy.org/en/latest/naming.html
"""

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

_T = TypeVar("_T", bound=Any)


meta = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
Base = declarative_base(metadata=meta)


class AwaitAttrs:
    class _AwaitAttrGetitem:
        __slots__ = "_instance"

        def __init__(self, _instance: Any):
            self._instance = _instance

        def __getattr__(self, name: str) -> Awaitable[Any]:
            return greenlet_spawn(getattr, self._instance, name)

    @property
    def await_attr(self) -> _AwaitAttrGetitem:
        """provide awaitable attribute access"""
        return AwaitAttrs._AwaitAttrGetitem(self)

    async def await_load(self, attr: Mapped[_T]) -> _T:
        """typed version of getattr"""
        return await greenlet_spawn(getattr, self, attr.key)


class BaseOrm(AwaitAttrs, Base):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=datetime.now(tz=timezone.utc),
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )
