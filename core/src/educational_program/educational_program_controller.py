from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response
from fastapi.responses import StreamingResponse
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.auth.auth_service import AuthService
from src.config.settings import get_settings
from src.educational_program.educational_program_schema import (
    EducationalProgramActiveExportRequestSchema,
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
        self.auth_service = AuthService(
            lang=lang,
            back=back,
            session=session,
        )

    @educational_program_router.get("/hierarchy", tags=["educational_program"])
    @try_rollback
    async def educational_program_hierarchy(
        self,
        request: Request,
        response: Response,
        educational_program_id: int = Query(..., description="Educational program ID"),
    ) -> EducationalProgramHierarchyViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.educational_program_service.educational_program_hierarchy(
            educational_program_id=educational_program_id,
        )

    @educational_program_router.get("/get", tags=["educational_program"])
    @try_rollback
    async def educational_program_get(
        self,
        request: Request,
        response: Response,
    ) -> EducationalProgramGetViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.educational_program_service.educational_program_get()

    @educational_program_router.get("/active/get", tags=["educational_program"])
    @try_rollback
    async def educational_program_active_get(
        self,
        request: Request,
        response: Response,
        field_of_study_id: int = Query(None, description="Field of Study ID for filtering"),
        start_year: int = Query(None, description="Start year for filtering"),
        end_year: int = Query(None, description="End year for filtering"),
        include_tag_ids: list[int] = Query(None, description="Tag IDs to include"),
        exclude_tag_ids: list[int] = Query(None, description="Tag IDs to exclude"),
        include_logic: str = Query("AND", description="AND or OR for include tags"),
        exclude_logic: str = Query("OR", description="AND or OR for exclude tags"),
    ) -> EducationalProgramActiveViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        filter = EducationalProgramGetFilterSchema(
            field_of_study_id=field_of_study_id,
            start_year=start_year,
            end_year=end_year,
            include_tag_ids=include_tag_ids or [],
            exclude_tag_ids=exclude_tag_ids or [],
            include_logic=include_logic,
            exclude_logic=exclude_logic,
        )
        return await self.educational_program_service.educational_program_active_get(
            filter=filter,
        )

    @educational_program_router.post("/active/export/excel", tags=["educational_program"])
    @try_rollback
    async def educational_program_active_export_excel(
        self,
        request: Request,
        response: Response,
        data: EducationalProgramActiveExportRequestSchema,
    ):
        await self.auth_service.admin_required(request=request, response=response)
        file_bytes = (
            await self.educational_program_service.educational_program_active_export_excel(
                payload=data,
            )
        )
        return StreamingResponse(
            content=iter([file_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=educational_program_active.xlsx"
            },
        )

    @educational_program_router.post("/add", tags=["educational_program"])
    @try_rollback
    async def educational_program_add(
        self,
        request: Request,
        response: Response,
        data: EducationalProgramAddSchema,
    ) -> AddViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.educational_program_service.educational_program_add(
            data=data,
        )

    @educational_program_router.patch("/update", tags=["educational_program"])
    @try_rollback
    async def educational_program_update(
        self,
        request: Request,
        response: Response,
        data: EducationalProgramUpdateSchema,
    ) -> SuccessSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.educational_program_service.educational_program_update(
            data=data,
        )

    @educational_program_router.delete("/delete", tags=["educational_program"])
    @try_rollback
    async def educational_program_delete(
        self,
        request: Request,
        response: Response,
        educational_program_id: int,
        delete_behavior: DeleteBehaviorEnum = Query(
            default=DeleteBehaviorEnum.RESTRICT,
            description="""Поведение дочерних ОП при удалении: RESTRICT -
            запретить удаление, если есть дочерние ОП; CASCADE - удалить все
            дочерние ОП; SET NULL - установить значение NULL в дочерних ОП
            (Теперь эти ОП будут считаться начальными в своей иерархии)""",
        ),
    ) -> SuccessSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.educational_program_service.educational_program_delete(
            educational_program_id=educational_program_id,
            delete_behavior=delete_behavior,
        )
