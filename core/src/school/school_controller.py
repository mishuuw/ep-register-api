from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.school.school_schema import (
    SchoolGetViewSchema,
    SchoolSchema,
    SchoolUpdateSchema,
)
from src.school.school_service import SchoolService
from src.common.token_service import token_service
from src.config.settings import get_settings
from src.user.user_schema import UserSchema
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

school_router = APIRouter()
settings = get_settings()


@cbv(school_router)
class SchoolController:
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

        self.school_service = SchoolService(
            lang=lang,
            back=back,
            session=session,
        )

    @school_router.get("/get", tags=["school"])
    @try_rollback
    async def school_get(
        self,
    #    _: UserSchema = Depends(token_service.admin_required),
    ) -> SchoolGetViewSchema:
        return await self.school_service.school_get()


    @school_router.post("/add", tags=["school"])
    @try_rollback
    async def school_add(
        self,
        data: SchoolSchema,
    #    _: UserSchema = Depends(token_service.admin_required),
    ) -> AddViewSchema:
        return await self.school_service.school_add(data = data)
    
    @school_router.patch("/update", tags=["school"])
    @try_rollback
    async def school_update(
        self,
        data: SchoolUpdateSchema
    #    _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        return await self.school_service.school_update(data = data)


    @school_router.delete("/delete", tags=["school"])
    @try_rollback
    async def school_delete(
        self,
        school_id: int = Query(..., description="School ID"),
    #    _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        return await self.school_service.school_delete(school_id=school_id)
