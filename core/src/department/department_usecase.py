from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.department.department_repo import DepartmentRepository


class DepartmentUsecase:
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
        self.department_repo = DepartmentRepository(
            lang=lang,
            back=back,
            session=session,
        )
