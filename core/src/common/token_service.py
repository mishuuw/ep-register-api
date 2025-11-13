from typing import Literal
from fastapi import Depends, Header, Request
from jwt import decode, encode
from sqlalchemy import select
from src.common.common_exc import (
    InvalidHttpException,
    NotAllowedHttpException,
    NotFoundHttpException,
)
from src.config.settings import get_settings
from src.models.enum import AccessLevelEnum
from src.models.user import UserOrm
from src.user.user_schema import UserSchema
from src.utils.db_util import get_session_obj

settings = get_settings()


class TokenService:
    def __init__(
        self,
        lang: Literal["ru", "en"],
    ):
        self.lang = lang

    async def validate_token(
        self,
        token: str,
    ) -> dict:
        try:
            data = decode(
                jwt=token,
                key=settings.SECRET_AUTH,
                algorithms=[settings.ALGORITHM],
            )
            return data
        except Exception:
            raise InvalidHttpException(name="token")

    async def type_required(
        self,
        request: Request,
        type_req: AccessLevelEnum,
        auth: str
    ) -> bool:
        if request.headers.get("cookie", None) is not None:
            all_cookies = [
                x for x in request.headers.get("cookie").split("; ")
            ]
            r_cookies = [
                y for y in all_cookies if settings.EP_REGISTER_COOKIE_NAME in y
            ]

        else:
            all_cookies = []
            r_cookies = []

        if r_cookies != []:
            auth_cookie = r_cookies[0].split("=")[1]
            token = auth_cookie

        else:
            auth_cookie = None
            token = auth
        
        data = await self.validate_token(token=token)
        
        roles = data.get("roles", None)
        if not roles:
            raise NotFoundHttpException(name="user")
        if type_req.value not in roles:
            raise NotAllowedHttpException(name="user")
        return True

    async def manager_required(
        self,
        request: Request,
        auth: str = Header(None)
    ) -> bool:
        return await self.type_required(
            request=request,
            type_req=AccessLevelEnum.manager,
            auth=auth,
        )

    async def director_required(
        self,
        request: Request,
        auth: str = Header(None)
    ) -> bool:
        return await self.type_required(
            request=request,
            type_req=AccessLevelEnum.director,
            auth=auth,
        )

    async def admin_required(
        self,
        request: Request,
        auth: str = Header(None)
    ) -> bool:
        return await self.type_required(
            request=request,
            type_req=AccessLevelEnum.admin,
            auth=auth,
        )
        
token_service = TokenService(
    lang="ru",
)