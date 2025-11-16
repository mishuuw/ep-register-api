from sqlalchemy import select
from typing import Literal, Tuple

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import get_settings
from src.educational_program.educational_program_schema import (
    EducationalProgramGetSchema,
    EducationalProgramGetViewSchema,
)
from src.models.degree import DegreeOrm
from src.models.educational_program import EducationalProgramOrm
from src.models.educational_program_partner import EducationalProgramPartnerOrm
from src.models.school import SchoolOrm

settings = get_settings()


class EducationalProgramRepository:
    def __init__(
        self,
        lang: Literal["ru", "en"],
        back: BackgroundTasks,
        session: AsyncSession,
    ):
        self.lang = lang
        self.back = back
        self.session = session

    async def educational_program_get(
        self,
    ) -> EducationalProgramGetViewSchema:
        query = (
            select(
                EducationalProgramOrm,
                SchoolOrm,
                DegreeOrm,
                EducationalProgramPartnerOrm,
            )
            .outerjoin(SchoolOrm, SchoolOrm.id == EducationalProgramOrm.school_id)
            .outerjoin(DegreeOrm, DegreeOrm.id == EducationalProgramOrm.degree_id)
            .outerjoin(
                EducationalProgramPartnerOrm,
                EducationalProgramPartnerOrm.id == EducationalProgramOrm.partner_id,
            )
        )
        result: list[
            Tuple[
                EducationalProgramOrm,
                SchoolOrm,
                DegreeOrm,
                EducationalProgramPartnerOrm,
            ]
        ] = (await self.session.execute(query)).all()

        return EducationalProgramGetViewSchema(
            count=len(result),
            result=[
                EducationalProgramGetSchema(
                    title=ep.title,
                    degree_title=deg.title if deg is not None else None,
                    partner_title=partner.title if partner is not None else None,
                    school_title=school.title if school is not None else None,
                    id=ep.id,
                    network_form=ep.network_form,
                    educational_form=ep.educational_form,
                    educational_standard_type=ep.educational_standard_type,
                    language=ep.language,
                    language_hours=ep.language_hours,
                    curriculum_number=ep.curriculum_number,
                    standard_duration_months=ep.standard_duration_months,
                    poa_accreditation_expiry=ep.poa_accreditation_expiry,
                    state_accreditation_expiry=ep.state_accreditation_expiry,
                    description=ep.description,
                )
                for ep, school, deg, partner in result
            ],
        )
