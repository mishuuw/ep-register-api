from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.educational_program_partner.educational_program_partner_repo import (
    EducationalProgramPartnerRepository,
)


class EducationalProgramPartnerUsecase:
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
        self.educational_program_partner_repo = EducationalProgramPartnerRepository(
            lang=lang,
            back=back,
            session=session,
        )
