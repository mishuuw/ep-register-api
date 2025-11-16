from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.common.token_service import token_service
from src.config.settings import get_settings
from src.educational_program.educational_program_schema import (
    EducationalProgramActiveViewSchema,
    EducationalProgramAddSchema,
    EducationalProgramGetFilterSchema,
    EducationalProgramGetViewSchema,
    EducationalProgramHierarchyViewSchema,
    EducationalProgramUpdateSchema,
)
from src.educational_program.educational_program_service import (
    EducationalProgramService,
)
from src.models.enum import DeleteBehaviorEnum
from src.user.user_schema import UserSchema
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

educational_program_router = APIRouter()
settings = get_settings()


@cbv(educational_program_router)
class EducationalProgramController:
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

        self.educational_program_service = EducationalProgramService(
            lang=lang,
            back=back,
            session=session,
        )

    @educational_program_router.get("/hierarchy", tags=["educational_program"])
    @try_rollback
    async def educational_program_hierarchy(
        self,
        educational_program_id: int = Query(..., description="Educational program ID"),
        _: UserSchema = Depends(token_service.admin_required),
    ) -> EducationalProgramHierarchyViewSchema:
        pass

    @educational_program_router.get("/get", tags=["educational_program"])
    @try_rollback
    async def educational_program_get(
        self,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> EducationalProgramGetViewSchema:
        return await self.educational_program_service.educational_program_get()

    @educational_program_router.get("/active/get", tags=["educational_program"])
    @try_rollback
    async def educational_program_active_get(
        self,
        filter: EducationalProgramGetFilterSchema = Depends(),
        _: UserSchema = Depends(token_service.admin_required),
    ) -> EducationalProgramActiveViewSchema:
        return await self.educational_program_service.educational_program_active_get(
            filter=filter,
        )

    @educational_program_router.post("/add", tags=["educational_program"])
    @try_rollback
    async def educational_program_add(
        self,
        data: EducationalProgramAddSchema,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> AddViewSchema:
        pass

    @educational_program_router.patch("/update", tags=["educational_program"])
    @try_rollback
    async def educational_program_update(
        self,
        data: EducationalProgramUpdateSchema,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> SuccessSchema:
        pass

    @educational_program_router.delete("/delete", tags=["educational_program"])
    @try_rollback
    async def educational_program_delete(
        self,
        educational_program_id: int,
        delete_behavior: DeleteBehaviorEnum = Query(
            default=DeleteBehaviorEnum.RESTRICT,
            description="""Поведение дочерних ОП при удалении: RESTRICT -
            запретить удаление, если есть дочерние ОП; CASCADE - удалить все
            дочерние ОП; SET NULL - установить значение NULL в дочерних ОП
            (Теперь эти ОП будут считаться начальными в своей иерархии)""",
        ),
        _: UserSchema = Depends(token_service.admin_required),
    ) -> SuccessSchema:
        pass
