from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.field_of_study.field_of_study_schema import (
    FieldOfStudyGetViewSchema,
    FieldOfStudySchema,
    FieldOfStudyUpdateSchema,
)
from src.field_of_study.field_of_study_service import FieldOfStudyService
from src.common.token_service import token_service
from src.config.settings import get_settings
from src.user.user_schema import UserSchema
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

field_of_study_router = APIRouter()
settings = get_settings()


@cbv(field_of_study_router)
class FieldOfStudyController:
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

        self.field_of_study_service = FieldOfStudyService(
            lang=lang,
            back=back,
            session=session,
        )

    @field_of_study_router.get("/get", tags=["field_of_study"])
    @try_rollback
    async def field_of_study_get(
        self,
    ) -> FieldOfStudyGetViewSchema:
        return await self.field_of_study_service.field_of_study_get()


    @field_of_study_router.post("/add", tags=["field_of_study"])
    @try_rollback
    async def field_of_study_add(
        self,
        data: FieldOfStudySchema,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> AddViewSchema:
        return await self.field_of_study_service.field_of_study_add(data=data)
    
    @field_of_study_router.patch("/update", tags=["field_of_study"])
    @try_rollback
    async def field_of_study_update(
        self,
        data: FieldOfStudyUpdateSchema,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        return await self.field_of_study_service.field_of_study_update(data=data)


    @field_of_study_router.delete("/delete", tags=["field_of_study"])
    @try_rollback
    async def field_of_study_delete(
        self,
        field_of_study_id: int = Query(..., description="Field of Study ID"),
        _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        return await self.field_of_study_service.field_of_study_delete(field_of_study_id=field_of_study_id)
