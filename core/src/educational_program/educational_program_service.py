from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.educational_program.educational_program_repo import (
    EducationalProgramRepository,
)
from src.educational_program.educational_program_schema import (
    EducationalProgramActiveViewSchema,
    EducationalProgramGetFilterSchema,
    EducationalProgramGetViewSchema,
)
from src.educational_program.educational_program_usecase import (
    EducationalProgramUsecase,
)


class EducationalProgramService:
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
        self.educational_program_usecase = EducationalProgramUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.educational_program_repo = EducationalProgramRepository(
            lang=lang,
            back=back,
            session=session,
        )

    async def educational_program_active_get(
        self,
        filter: EducationalProgramGetFilterSchema,
    ) -> EducationalProgramActiveViewSchema:
        result = await self.educational_program_repo.educational_program_active_get(
            filter=filter,
        )

        return result

    async def educational_program_get(
        self,
    ) -> EducationalProgramGetViewSchema:
        result = await self.educational_program_repo.educational_program_get()

        return result
