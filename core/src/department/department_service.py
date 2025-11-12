from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.department.department_schema import (
    DepartmentAddSchema,
    DepartmentGetSchema,
    DepartmentGetViewSchema,
)
from src.department.department_usecase import DepartmentUsecase
from src.department.department_repo import DepartmentRepository
from src.models.user import UserOrm
from src.utils.common_util import timeit


class DepartmentService:
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
        self.department_usecase = DepartmentUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.department_repo = DepartmentRepository(
            lang=lang,
            back=back,
            session=session,
        )