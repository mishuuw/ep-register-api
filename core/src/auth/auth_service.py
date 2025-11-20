from typing import Literal

from fastapi import BackgroundTasks, Request, Response
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_schema import CredentialsSchema
from src.common.common_exc import InvalidHttpException
from src.common.common_repo import CommonRepository
from src.auth.auth_usecase import AuthUsecase
from src.common.common_schema import SuccessSchema
from src.config.settings import get_settings
from src.models.enum import AccessLevelEnum

settings = get_settings()


class AuthService:
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
        self.auth_usecase = AuthUsecase(
            session=session,
            back=back,
            lang=lang,
        )

    async def type_required(
        self,
        request: Request,
        type_req: AccessLevelEnum,
        response: Response,
    ) -> bool:
        return True  # dev
        """STRICT LOGIC: REQUIRE ACCESS TOKEN ON EVERY REQUEST, DONT ALLOW JUST REFRESH
        # bearer = request.headers.get("Authorization")
        # if not bearer:
        #     raise InvalidHttpException(name="auth")
        #
        # if str(bearer).lower().startswith("bearer "):
        #     bearer_token = bearer.split(" ", 1)[1]
        # else:
        #     bearer_token = bearer
        #
        # try:
        #     payload = await self.auth_usecase.verify_access_token(
        #         token=bearer_token
        #     )
        #     user_id = payload.get("sub")
        #     await self.auth_usecase.ensure_access_level(
        #         user_id=user_id,
        #         required=type_req,
        #     )
        #     return True
        # except ExpiredSignatureError:
        #     # Only here do we look at the refresh cookie.
        #     refresh_cookie_value = request.cookies.get(
        #         settings.EP_REGISTER_COOKIE_NAME
        #     )
        #     if not refresh_cookie_value:
        #         raise InvalidHttpException(name="auth")
        #
        #     user_id = await self.auth_usecase.verify_refresh_token(
        #         token=refresh_cookie_value
        #     )
        #     if not user_id:
        #         raise InvalidHttpException(name="refresh token")
        #
        #     access_token = await self.auth_usecase.create_access_token(
        #         user_id=user_id
        #     )
        #     response.headers["Authorization"] = f"Bearer {access_token}"
        #     await self.auth_usecase.ensure_access_level(
        #         user_id=user_id,
        #         required=type_req,
        #     )
        #     return True
        # except InvalidTokenError:
        #     raise InvalidHttpException(name="Bearer token")
        """
        bearer = request.headers.get("Authorization")
        # Prefer access token in Authorization header
        if bearer:
            if str(bearer).lower().startswith("bearer "):
                bearer_token = bearer.split(" ", 1)[1]
            else:
                bearer_token = bearer

            try:
                payload = await self.auth_usecase.verify_access_token(
                    token=bearer_token
                )
                user_id = payload.get("sub")

                await self.auth_usecase.ensure_access_level(
                    user_id=user_id,
                    required=type_req,
                )

                return True
            except ExpiredSignatureError:
                # Expired access is an expected condition; fall back to refresh.
                pass
            except InvalidTokenError:
                # Malformed / invalid token should not silently fall back.
                raise InvalidHttpException(name="Bearer token")

        # No valid access token, try refresh cookie via framework helper
        refresh_cookie_value = request.cookies.get(settings.EP_REGISTER_COOKIE_NAME)

        if not refresh_cookie_value:
            raise InvalidHttpException(name="auth")

        user_id = await self.auth_usecase.verify_refresh_token(
            token=refresh_cookie_value
        )
        if not user_id:
            raise InvalidHttpException(name="refresh token")

        # Issue a fresh access token from refresh
        access_token = await self.auth_usecase.create_access_token(user_id=user_id)
        response.headers["Authorization"] = f"Bearer {access_token}"
        return True

    async def manager_required(
        self,
        request: Request,
        response: Response,
    ) -> bool:
        return await self.type_required(
            request=request,
            type_req=AccessLevelEnum.manager,
            response=response,
        )

    async def director_required(
        self,
        request: Request,
        response: Response,
    ) -> bool:
        return await self.type_required(
            request=request,
            type_req=AccessLevelEnum.director,
            response=response,
        )

    async def admin_required(
        self,
        request: Request,
        response: Response,
    ) -> bool:
        return await self.type_required(
            request=request,
            type_req=AccessLevelEnum.admin,
            response=response,
        )

    async def authenticate_user(
        self, credentials: CredentialsSchema, response: Response
    ) -> SuccessSchema:
        result, refresh_token, access_token = await self.auth_usecase.authenticate_user(
            credentials=credentials
        )
        response.set_cookie(
            key=settings.EP_REGISTER_COOKIE_NAME,
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        response.headers["Authorization"] = f"Bearer {access_token}"

        return result
