from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.auth.auth_service import AuthService
from src.config.settings import get_settings
from src.field_of_study.field_of_study_schema import (
    FieldOfStudyGetViewSchema,
    FieldOfStudySchema,
    FieldOfStudyUpdateSchema,
)
from src.field_of_study.field_of_study_service import FieldOfStudyService
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
        self.auth_service = AuthService(
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
        request: Request,
        response: Response,
        data: FieldOfStudySchema,
    ) -> AddViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.field_of_study_service.field_of_study_add(data=data)

    @field_of_study_router.patch("/update", tags=["field_of_study"])
    @try_rollback
    async def field_of_study_update(
        self,
        request: Request,
        response: Response,
        data: FieldOfStudyUpdateSchema,
    ) -> None:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.field_of_study_service.field_of_study_update(data=data)

    @field_of_study_router.delete("/delete", tags=["field_of_study"])
    @try_rollback
    async def field_of_study_delete(
        self,
        request: Request,
        response: Response,
        field_of_study_id: int = Query(..., description="Field of Study ID"),
    ) -> None:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.field_of_study_service.field_of_study_delete(
            field_of_study_id=field_of_study_id
        )
