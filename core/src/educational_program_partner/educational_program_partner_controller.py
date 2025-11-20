from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.auth.auth_service import AuthService
from src.config.settings import get_settings
from src.educational_program_partner.educational_program_partner_schema import (
    EducationalProgramPartnerFilterSchema,
    EducationalProgramPartnerGetViewSchema,
    EducationalProgramPartnerSchema,
    EducationalProgramPartnerUpdateSchema,
)
from src.educational_program_partner.educational_program_partner_service import (
    EducationalProgramPartnerService,
)
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

educational_program_partner_router = APIRouter()
settings = get_settings()


@cbv(educational_program_partner_router)
class EducationalProgramPartnerController:
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

        self.educational_program_partner_service = EducationalProgramPartnerService(
            lang=lang,
            back=back,
            session=session,
        )
        self.auth_service = AuthService(
            lang=lang,
            back=back,
            session=session,
        )

    @educational_program_partner_router.get(
        "/get", tags=["educational_program_partner"]
    )
    @try_rollback
    async def educational_program_partner_get(
        self,
        request: Request,
        response: Response,
        filter: EducationalProgramPartnerFilterSchema = Depends(),
    ) -> EducationalProgramPartnerGetViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        service = self.educational_program_partner_service
        return await service.educational_program_partner_get(filter=filter)

    @educational_program_partner_router.post(
        "/add", tags=["educational_program_partner"]
    )
    @try_rollback
    async def educational_program_partner_add(
        self,
        request: Request,
        response: Response,
        data: EducationalProgramPartnerSchema,
    ) -> AddViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        service = self.educational_program_partner_service
        return await service.educational_program_partner_add(data=data)

    @educational_program_partner_router.patch(
        "/update", tags=["educational_program_partner"]
    )
    @try_rollback
    async def educational_program_partner_update(
        self,
        request: Request,
        response: Response,
        data: EducationalProgramPartnerUpdateSchema,
    ) -> SuccessSchema:
        await self.auth_service.admin_required(request=request, response=response)
        service = self.educational_program_partner_service
        return await service.educational_program_partner_update(data=data)

    @educational_program_partner_router.delete(
        "/delete", tags=["educational_program_partner"]
    )
    @try_rollback
    async def educational_program_partner_delete(
        self,
        request: Request,
        response: Response,
        educational_program_partner_id: int,
    ) -> SuccessSchema:
        await self.auth_service.admin_required(request=request, response=response)
        service = self.educational_program_partner_service
        return await service.educational_program_partner_delete(
            educational_program_partner_id=educational_program_partner_id
        )
