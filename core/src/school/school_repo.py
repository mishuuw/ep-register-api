from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import get_settings

settings = get_settings()


class SchoolRepository:
    def __init__(
        self,
        lang: Literal["ru", "en"],
        back: BackgroundTasks,
        session: AsyncSession,
    ):
        self.lang = lang
        self.back = back
        self.session = session
