from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Response
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.auth_schema import CredentialsSchema
from src.common.common_schema import SuccessSchema
from src.config.settings import get_settings
from src.auth.auth_service import AuthService
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

auth_router = APIRouter()
settings = get_settings()


@cbv(auth_router)
class AuthController:
    def __init__(
        self,
        back: BackgroundTasks,
        session: AsyncSession = Depends(get_session_obj),
        lang: Literal["ru", "en"] = Query(
            default="ru",
            description="Language code",
        ),
    ):
        self.lang = lang
        self.back = back
        self.session = session

        self.auth_service = AuthService(
            lang=lang,
            back=back,
            session=session,
        )

    @auth_router.post("/login", tags=["auth"])
    @try_rollback
    async def auth_get(
        self,
        credentials: CredentialsSchema,
        response: Response,
    ) -> SuccessSchema:
        return await self.auth_service.authenticate_user(
            credentials=credentials, response=response
        )
