from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.school.school_schema import (
    SchoolAddSchema,
    SchoolGetSchema,
    SchoolGetViewSchema,
)
from src.school.school_usecase import SchoolUsecase
from src.school.school_repo import SchoolRepository
from src.models.user import UserOrm
from src.utils.common_util import timeit


class SchoolService:
    def __init__(
        self,
        session: AsyncSession,
        back: BackgroundTasks,
        lang: Literal["ru", "en"],
    ):
        self.lang = lang
        self.back = back
        self.session = session

        self.common_repo = CommonRepository(session=session)
        self.school_usecase = SchoolUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.school_repo = SchoolRepository(
            lang=lang,
            back=back,
            session=session,
        )
