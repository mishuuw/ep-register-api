from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.auth.auth_service import AuthService
from src.config.settings import get_settings
from src.user.user_schema import UserGetViewSchema, UserSchema, UserUpdateSchema
from src.user.user_service import UserService
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

user_router = APIRouter()
settings = get_settings()


@cbv(user_router)
class UserController:
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

        self.user_service = UserService(
            lang=lang,
            back=back,
            session=session,
        )
        self.auth_service = AuthService(
            lang=lang,
            back=back,
            session=session,
        )

    @user_router.get("/get", tags=["user"])
    @try_rollback
    async def user_get(
        self,
        request: Request,
        response: Response,
    ) -> UserGetViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.user_service.user_get()

    @user_router.post("/add", tags=["user"])
    @try_rollback
    async def user_add(
        self,
        request: Request,
        response: Response,
        data: UserSchema,
    ) -> AddViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.user_service.user_add(
            data=data,
        )

    @user_router.patch("/update", tags=["user"])
    @try_rollback
    async def user_update(
        self,
        request: Request,
        response: Response,
        data: UserUpdateSchema,
    ) -> None:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.user_service.user_update(
            data=data,
        )

    @user_router.delete("/delete", tags=["user"])
    @try_rollback
    async def user_delete(
        self,
        request: Request,
        response: Response,
        user_id: int = Query(
            ...,
            description="User ID",
        ),
    ) -> None:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.user_service.user_delete(
            user_id=user_id,
        )
