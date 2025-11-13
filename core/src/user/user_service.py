from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.user.user_usecase import UserUsecase
from src.user.user_repo import UserRepository
from src.models.user import UserOrm
from src.utils.common_util import timeit


class UserService:
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
        self.user_usecase = UserUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.user_repo = UserRepository(
            lang=lang,
            back=back,
            session=session,
        )
