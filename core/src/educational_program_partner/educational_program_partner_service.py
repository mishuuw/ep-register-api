from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.educational_program_partner.educational_program_partner_schema import (
    EducationalProgramPartnerAddSchema,
    EducationalProgramPartnerGetSchema,
    EducationalProgramPartnerGetViewSchema,
)
from src.educational_program_partner.educational_program_partner_usecase import EducationalProgramPartnerUsecase
from src.educational_program_partner.educational_program_partner_repo import EducationalProgramPartnerRepository
from src.models.user import UserOrm
from src.utils.common_util import timeit


class EducationalProgramPartnerService:
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
        self.educational_program_partner_usecase = EducationalProgramPartnerUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.educational_program_partner_repo = EducationalProgramPartnerRepository(
            lang=lang,
            back=back,
            session=session,
        )
