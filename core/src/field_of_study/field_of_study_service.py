from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.field_of_study.field_of_study_schema import (
    FieldOfStudyAddSchema,
    FieldOfStudyGetSchema,
    FieldOfStudyGetViewSchema,
)
from src.field_of_study.field_of_study_usecase import FieldOfStudyUsecase
from src.field_of_study.field_of_study_repo import FieldOfStudyRepository
from src.models.user import UserOrm
from src.utils.common_util import timeit


class FieldOfStudyService:
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
        self.field_of_study_usecase = FieldOfStudyUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.field_of_study_repo = FieldOfStudyRepository(
            lang=lang,
            back=back,
            session=session,
        )