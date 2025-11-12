from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.degree.degree_schema import (
    DegreeAddSchema,
    DegreeGetSchema,
    DegreeGetViewSchema,
)
from src.degree.degree_usecase import DegreeUsecase
from src.degree.degree_repo import DegreeRepository
from src.models.user import UserOrm
from src.utils.common_util import timeit


class DegreeService:
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
        self.degree_usecase = DegreeUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.degree_repo = DegreeRepository(
            lang=lang,
            back=back,
            session=session,
        )