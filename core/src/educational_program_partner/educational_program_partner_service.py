from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_
from src.common.common_exc import NotFoundHttpException
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.educational_program_partner.educational_program_partner_repo import (
    EducationalProgramPartnerRepository,
)
from src.educational_program_partner.educational_program_partner_schema import (
    EducationalProgramPartnerFilterSchema,
    EducationalProgramPartnerGetSchema,
    EducationalProgramPartnerGetViewSchema,
    EducationalProgramPartnerSchema,
    EducationalProgramPartnerUpdateSchema,
)
from src.educational_program_partner.educational_program_partner_usecase import (
    EducationalProgramPartnerUsecase,
)
from src.models.educational_program_partner import EducationalProgramPartnerOrm


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

    async def educational_program_partner_delete(
        self,
        educational_program_partner_id: int,
    ) -> SuccessSchema:
        educational_program_partner = await self.common_repo.get_one(
            EducationalProgramPartnerOrm,
            EducationalProgramPartnerOrm.id == educational_program_partner_id,
        )
        if not educational_program_partner:
            raise NotFoundHttpException(name="Educational Program Partner")

        await self.common_repo.delete(
            EducationalProgramPartnerOrm,
            EducationalProgramPartnerOrm.id == educational_program_partner.id,
        )
        return SuccessSchema(detail="success")

    async def educational_program_partner_update(
        self,
        data: EducationalProgramPartnerUpdateSchema,
    ) -> SuccessSchema:
        educational_program_partner = await self.common_repo.get_one(
            EducationalProgramPartnerOrm,
            EducationalProgramPartnerOrm.id == data.id,
        )
        if not educational_program_partner:
            raise NotFoundHttpException(name="Educational Program Partner")

        data_dict = data.model_dump(exclude_unset=True)

        # Проверяем, есть ли что обновлять
        if not data_dict:
            return SuccessSchema(detail="success")

        await self.common_repo.update(
            EducationalProgramPartnerOrm(
                **data_dict,
            )
        )
        return SuccessSchema(detail="success")

    async def educational_program_partner_add(
        self,
        data: EducationalProgramPartnerSchema,
    ) -> AddViewSchema:
        educational_program_partner = await self.common_repo.add(
            EducationalProgramPartnerOrm(
                title=data.title,
                partner_type=data.partner_type,
                hours=data.hours,
            )
        )
        return AddViewSchema(id=educational_program_partner.id)

    async def educational_program_partner_get(
        self,
        filter: EducationalProgramPartnerFilterSchema,
    ) -> EducationalProgramPartnerGetViewSchema:
        filters = []
        if filter.partner_type is not None:
            filters.append(
                EducationalProgramPartnerOrm.partner_type == filter.partner_type
            )

        educational_program_partners = await self.common_repo.get_all_scalars(
            EducationalProgramPartnerOrm,
            and_(*filters) if filters else True,
        )

        return EducationalProgramPartnerGetViewSchema(
            count=len(educational_program_partners),
            result=[
                EducationalProgramPartnerGetSchema(
                    id=partner.id,
                    title=partner.title,
                    partner_type=partner.partner_type,
                    hours=partner.hours,
                )
                for partner in educational_program_partners
            ],
        )
