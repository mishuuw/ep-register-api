from collections import defaultdict
from sqlalchemy import select, and_
from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import get_settings
from src.educational_program.educational_program_schema import (
    EducationalProgramActiveSchema,
    EducationalProgramActiveViewSchema,
    EducationalProgramGetFilterSchema,
    EducationalProgramGetSchema,
    EducationalProgramGetViewSchema,
)
from src.models.degree import DegreeOrm
from src.models.educational_program import (
    EducationalProgramActiveOrm,
    EducationalProgramOrm,
    EducationalProgramToPartnerOrm,
)
from src.models.educational_program_partner import EducationalProgramPartnerOrm
from src.models.field_of_study import FieldOfStudyOrm
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

    async def _get_partners_by_program_ids(
        self, program_ids: list[int]
    ) -> dict[int, list[str]]:
        if not program_ids:
            return {}
        rows = (
            await self.session.execute(
                select(EducationalProgramToPartnerOrm, EducationalProgramPartnerOrm)
                .where(
                    EducationalProgramToPartnerOrm.educational_program_id.in_(
                        program_ids
                    )
                )
                .join(
                    EducationalProgramPartnerOrm,
                    EducationalProgramPartnerOrm.id
                    == EducationalProgramToPartnerOrm.partner_id,
                )
            )
        ).all()
        grouped: dict[int, set[str]] = defaultdict(set)
        for junction, partner in rows:
            if partner is not None:
                grouped[junction.educational_program_id].add(partner.title)
        return {
            program_id: sorted(partner_titles)
            for program_id, partner_titles in grouped.items()
        }

    async def educational_program_active_get(
        self,
        filter: EducationalProgramGetFilterSchema,
    ) -> EducationalProgramActiveViewSchema:
        filters = []
        if filter.start_year is not None:
            filters.append(EducationalProgramActiveOrm.start_year == filter.start_year)
        if filter.end_year is not None:
            filters.append(EducationalProgramActiveOrm.end_year == filter.end_year)
        if filter.field_of_study_id is not None:
            filters.append(
                EducationalProgramActiveOrm.field_of_study_id
                == filter.field_of_study_id
            )

        query = select(
            EducationalProgramActiveOrm,
            FieldOfStudyOrm,
            EducationalProgramOrm,
            SchoolOrm,
            DegreeOrm,
        )
        if filters:
            query = query.where(and_(*filters))
        query = (
            query.join(
                EducationalProgramOrm,
                EducationalProgramOrm.id
                == EducationalProgramActiveOrm.educational_program_id,
            )
            .join(
                FieldOfStudyOrm,
                FieldOfStudyOrm.id == EducationalProgramActiveOrm.field_of_study_id,
            )
            .outerjoin(SchoolOrm, SchoolOrm.id == EducationalProgramOrm.school_id)
            .outerjoin(DegreeOrm, DegreeOrm.id == EducationalProgramOrm.degree_id)
        )

        result = (await self.session.execute(query)).all()
        active_ids = {epa.id for epa, *_ in result}
        partner_map = await self._get_partners_by_program_ids(
            sorted({ep.id for _, _, ep, _, _ in result})
        )

        schemas = []
        for epa, f_o_s, ep, school, deg in result:
            schemas.append(
                EducationalProgramActiveSchema(
                    field_of_study_title=f_o_s.title,
                    field_of_study_code=f_o_s.code,
                    start_year=epa.start_year,
                    end_year=epa.end_year,
                    title=ep.title,
                    title_short=ep.title_short,
                    degree_title=deg.title if deg is not None else None,
                    partner_titles=partner_map.get(ep.id, []),
                    school_title=school.title if school is not None else None,
                    school_code=school.code if school is not None else None,
                    id=ep.id,
                    network_form=ep.network_form,
                    educational_form=ep.educational_form,
                    educational_standard_type=ep.educational_standard_type,
                    language=ep.language,
                    language_hours=ep.language_hours,
                    standard_duration_months=ep.standard_duration_months,
                    poa_accreditation_expiry=ep.poa_accreditation_expiry,
                    poa_accreditation_company=ep.poa_accreditation_company,
                    state_accreditation_expiry=ep.state_accreditation_expiry,
                    description=ep.description,
                )
            )

        return EducationalProgramActiveViewSchema(
            count=len(active_ids),
            result=schemas,
        )

    async def educational_program_get(
        self,
    ) -> EducationalProgramGetViewSchema:
        query = (
            select(
                EducationalProgramOrm,
                SchoolOrm,
                DegreeOrm,
            )
            .outerjoin(SchoolOrm, SchoolOrm.id == EducationalProgramOrm.school_id)
            .outerjoin(DegreeOrm, DegreeOrm.id == EducationalProgramOrm.degree_id)
        )
        result = (await self.session.execute(query)).all()
        partner_map = await self._get_partners_by_program_ids(
            sorted({ep.id for ep, *_ in result})
        )

        schemas = []
        for ep, school, deg in result:
            schemas.append(
                EducationalProgramGetSchema(
                    title=ep.title,
                    title_short=ep.title_short,
                    degree_title=deg.title if deg is not None else None,
                    school_title=school.title if school is not None else None,
                    school_code=school.code if school is not None else None,
                    partner_titles=partner_map.get(ep.id, []),
                    id=ep.id,
                    network_form=ep.network_form,
                    educational_form=ep.educational_form,
                    educational_standard_type=ep.educational_standard_type,
                    language=ep.language,
                    language_hours=ep.language_hours,
                    standard_duration_months=ep.standard_duration_months,
                    poa_accreditation_expiry=ep.poa_accreditation_expiry,
                    poa_accreditation_company=ep.poa_accreditation_company,
                    state_accreditation_expiry=ep.state_accreditation_expiry,
                    description=ep.description,
                )
            )

        return EducationalProgramGetViewSchema(
            count=len({ep.id for ep, *_ in result}),
            result=schemas,
        )
