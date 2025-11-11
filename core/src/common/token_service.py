from typing import Literal

from fastapi import Header, Request
from jwt import decode, encode
from src.common.common_exc import (
    InvalidHttpException,
    NotAllowedHttpException,
    NotFoundHttpException,
)
from src.config.settings import get_settings
from src.user.user_schema import UserSchema

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
        auth: str,
        types=[],
    ) -> UserSchema:
        pass

    async def manager_required(
        self,
        request: Request,
        auth: str = Header(None)
    ) -> UserSchema:
        pass

    async def director_required(
        self,
        request: Request,
        auth: str = Header(None)
    ) -> UserSchema:
        pass

    async def admin_required(
        self,
        request: Request,
        auth: str = Header(None)
    ) -> UserSchema:
        pass


token_service = TokenService(lang="ru")
