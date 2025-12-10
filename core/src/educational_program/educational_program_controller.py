from typing import Literal, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response
from src.common.common_exc import WrongParametersHttpException
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.auth.auth_service import AuthService
from src.config.settings import get_settings
from src.educational_program.educational_program_schema import (
    EducationalProgramActiveViewSchema,
    EducationalProgramAddSchema,
    EducationalProgramGetFilterSchema,
    EducationalProgramGetViewSchema,
    EducationalProgramHierarchyViewSchema,
    EducationalProgramUpdateSchema,
    EducationalProgramActiveGetFilterSchema
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
        filter: EducationalProgramGetFilterSchema = Depends(),
        partner_ids: Optional[List[int]] = Query(
            default=None,
            description="List of partner IDs for filtering",
        ),
        no_partners: Optional[bool] = Query(
            default=None,
            description="If true, return programs that have no partners",
        ),
    ) -> EducationalProgramGetViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        
        if partner_ids and no_partners:
            msg_en = "partner_ids and no_partners cannot be used together"
            msg_ru = "параметры partner_ids и no_partners нельзя использовать одновременно"
            raise WrongParametersHttpException(params=(msg_ru if self.lang == "ru" else msg_en), lang=self.lang)
        if filter.poa_accreditation_expiry is not None and filter.poa_accreditation_expiry_is_null:
            msg_en = "poa_accreditation_expiry and poa_accreditation_expiry_is_null cannot be used together"
            msg_ru = "Нельзя одновременно использовать poa_accreditation_expiry и poa_accreditation_expiry_is_null"
            raise WrongParametersHttpException(params=(msg_ru if self.lang == "ru" else msg_en), lang=self.lang)
        if filter.state_accreditation_expiry is not None and filter.state_accreditation_expiry_is_null:
            msg_en = "state_accreditation_expiry and state_accreditation_expiry_is_null cannot be used together"
            msg_ru = "Нельзя одновременно использовать state_accreditation_expiry и state_accreditation_expiry_is_null"
            raise WrongParametersHttpException(params=(msg_ru if self.lang == "ru" else msg_en), lang=self.lang)

        return await self.educational_program_service.educational_program_get(
            filter=filter,
            partner_ids=partner_ids,
            no_partners=no_partners,
        )

    @educational_program_router.get("/active/get", tags=["educational_program"])
    @try_rollback
    async def educational_program_active_get(
        self,
        request: Request,
        response: Response,
        filter: EducationalProgramActiveGetFilterSchema = Depends(),
        partner_ids: Optional[List[int]] = Query(
            default=None,
            description="List of partner IDs for filtering",
        ),
        no_partners: Optional[bool] = Query(
            default=None,
            description="If true, return programs that have no partners",
        ),
    ) -> EducationalProgramActiveViewSchema:
        await self.auth_service.admin_required(request=request, response=response)

        if partner_ids and no_partners:
            msg_en = "partner_ids and no_partners cannot be used together"
            msg_ru = "параметры partner_ids и no_partners нельзя использовать одновременно"
            raise WrongParametersHttpException(params=(msg_ru if self.lang == "ru" else msg_en), lang=self.lang)
        if filter.poa_accreditation_expiry is not None and filter.poa_accreditation_expiry_is_null:
            msg_en = "poa_accreditation_expiry and poa_accreditation_expiry_is_null cannot be used together"
            msg_ru = "Нельзя одновременно использовать poa_accreditation_expiry и poa_accreditation_expiry_is_null"
            raise WrongParametersHttpException(params=(msg_ru if self.lang == "ru" else msg_en), lang=self.lang)
        if filter.state_accreditation_expiry is not None and filter.state_accreditation_expiry_is_null:
            msg_en = "state_accreditation_expiry and state_accreditation_expiry_is_null cannot be used together"
            msg_ru = "Нельзя одновременно использовать state_accreditation_expiry и state_accreditation_expiry_is_null"
            raise WrongParametersHttpException(params=(msg_ru if self.lang == "ru" else msg_en), lang=self.lang)
        
        return await self.educational_program_service.educational_program_active_get(
            filter=filter,
            partner_ids=partner_ids,
            no_partners=no_partners,
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
