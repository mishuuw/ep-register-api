from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.common.token_service import token_service  # noqa
from src.config.settings import get_settings
from src.educational_program_partner.educational_program_partner_schema import (
    EducationalProgramPartnerAddSchema,
    EducationalProgramPartnerFilterSchema,
    EducationalProgramPartnerGetViewSchema,
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

    @educational_program_partner_router.get(
        "/get", tags=["educational_program_partner"]
    )
    @try_rollback
    async def educational_program_partner_get(
        self,
        filter: EducationalProgramPartnerFilterSchema = Depends(),
        #    _: UserSchema = Depends(token_service.admin_required),
    ) -> EducationalProgramPartnerGetViewSchema:
        pass

    @educational_program_partner_router.post(
        "/add", tags=["educational_program_partner"]
    )
    @try_rollback
    async def educational_program_partner_add(
        self,
        data: EducationalProgramPartnerAddSchema,
        #    _: UserSchema = Depends(token_service.admin_required),
    ) -> AddViewSchema:
        pass

    @educational_program_partner_router.patch(
        "/update", tags=["educational_program_partner"]
    )
    @try_rollback
    async def educational_program_partner_update(
        self,
        #    _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        pass

    @educational_program_partner_router.delete(
        "/delete", tags=["educational_program_partner"]
    )
    @try_rollback
    async def educational_program_partner_delete(
        self,
        #    _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        pass
