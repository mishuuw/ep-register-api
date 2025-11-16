from collections import defaultdict
from sqlalchemy import select, and_
from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.config.settings import get_settings
from src.educational_program.educational_program_schema import (
    EducationalProgramActiveSchema,
    EducationalProgramActiveViewSchema,
    EducationalProgramGetFilterSchema,
    EducationalProgramGetSchema,
    EducationalProgramGetViewSchema,
    EducationalProgramHierarchySchema,
    EducationalProgramHierarchyViewSchema,
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

    async def educational_program_hierarchy(
        self,
        educational_program_id: int,
    ) -> EducationalProgramHierarchyViewSchema:
        program_tree = (
            select(EducationalProgramOrm.id)
            .where(EducationalProgramOrm.id == educational_program_id)
            .cte(name="program_tree", recursive=True)
        )

        program_tree = program_tree.union_all(
            select(EducationalProgramOrm.id).where(
                EducationalProgramOrm.parent_id == program_tree.c.id
            )
        )

        query = (
            select(EducationalProgramOrm, SchoolOrm, DegreeOrm)
            .join(program_tree, EducationalProgramOrm.id == program_tree.c.id)
            .outerjoin(SchoolOrm, SchoolOrm.id == EducationalProgramOrm.school_id)
            .outerjoin(DegreeOrm, DegreeOrm.id == EducationalProgramOrm.degree_id)
            .order_by(EducationalProgramOrm.parent_id, EducationalProgramOrm.id)
        )
        rows = (await self.session.execute(query)).all()
        if not rows:
            raise NotFoundHttpException(name="образовательная программа")

        program_ids = [ep.id for ep, *_ in rows]
        unique_program_ids = sorted(set(program_ids))
        partner_map = await self._get_partners_by_program_ids(unique_program_ids)
        active_map = await self._get_latest_active_map(unique_program_ids)

        node_map: dict[int, EducationalProgramHierarchySchema] = {}
        parent_lookup: dict[int, int | None] = {}
        for ep, school, degree in rows:
            active_entry = active_map.get(ep.id)
            active, fos = active_entry if active_entry else (None, None)
            parent_lookup[ep.id] = ep.parent_id
            node_map[ep.id] = EducationalProgramHierarchySchema(
                parent_id=ep.parent_id,
                title=ep.title,
                title_short=ep.title_short,
                degree_title=degree.title if degree is not None else None,
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
                parent=None,
                children=[],
                is_active=active is not None,
                field_of_study_title=fos.title if fos is not None else None,
                field_of_study_code=fos.code if fos is not None else None,
                start_year=active.start_year if active is not None else None,
                end_year=active.end_year if active is not None else None,
            )

        for ep, _, _ in rows:
            if ep.parent_id and ep.parent_id in node_map:
                parent_schema = node_map[ep.parent_id]
                parent_schema.children.append(node_map[ep.id])

        root = node_map.get(educational_program_id)
        if root is None:
            raise NotFoundHttpException(
                lang=self.lang,
                name="образовательная программа",
                name_en="educational program",
            )

        ancestor_ids: list[int] = []
        current_parent_id = parent_lookup.get(educational_program_id)
        while current_parent_id is not None:
            ancestor_ids.append(current_parent_id)
            current_parent_id = await self.session.scalar(
                select(EducationalProgramOrm.parent_id).where(
                    EducationalProgramOrm.id == current_parent_id
                )
            )

        if ancestor_ids:
            ancestor_rows = (
                await self.session.execute(
                    select(EducationalProgramOrm, SchoolOrm, DegreeOrm)
                    .where(EducationalProgramOrm.id.in_(ancestor_ids))
                    .outerjoin(
                        SchoolOrm, SchoolOrm.id == EducationalProgramOrm.school_id
                    )
                    .outerjoin(
                        DegreeOrm, DegreeOrm.id == EducationalProgramOrm.degree_id
                    )
                )
            ).all()
            ancestor_row_map = {
                ep.id: (ep, school, degree) for ep, school, degree in ancestor_rows
            }
            ancestor_partner_map = await self._get_partners_by_program_ids(ancestor_ids)
            ancestor_active_map = await self._get_latest_active_map(ancestor_ids)

            parent_chain = None
            for ancestor_id in ancestor_ids:
                row = ancestor_row_map.get(ancestor_id)
                if row is None:
                    continue
                ep, school, degree = row
                active_entry = ancestor_active_map.get(ep.id)
                active, fos = active_entry if active_entry else (None, None)
                parent_chain = EducationalProgramHierarchySchema(
                    title=ep.title,
                    title_short=ep.title_short,
                    degree_title=degree.title if degree is not None else None,
                    school_title=school.title if school is not None else None,
                    school_code=school.code if school is not None else None,
                    partner_titles=ancestor_partner_map.get(ep.id, []),
                    id=ep.id,
                    parent_id=ep.parent_id,
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
                    parent=parent_chain,
                    children=[],
                    is_active=active is not None,
                    field_of_study_title=fos.title if fos is not None else None,
                    field_of_study_code=fos.code if fos is not None else None,
                    start_year=active.start_year if active is not None else None,
                    end_year=active.end_year if active is not None else None,
                )
            root.parent = parent_chain

        return EducationalProgramHierarchyViewSchema(
            count=len(set(node_map.keys()) | set(ancestor_ids)),
            result=[root],
        )

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

    async def _get_latest_active_map(
        self, program_ids: list[int]
    ) -> dict[int, tuple[EducationalProgramActiveOrm, FieldOfStudyOrm]]:
        if not program_ids:
            return {}
        rows = (
            await self.session.execute(
                select(EducationalProgramActiveOrm, FieldOfStudyOrm)
                .outerjoin(
                    FieldOfStudyOrm,
                    FieldOfStudyOrm.id == EducationalProgramActiveOrm.field_of_study_id,
                )
                .where(
                    EducationalProgramActiveOrm.educational_program_id.in_(program_ids)
                )
            )
        ).all()
        active_map: dict[int, tuple[EducationalProgramActiveOrm, FieldOfStudyOrm]] = {}
        for active, fos in rows:
            current = active_map.get(active.educational_program_id)
            if current is None or active.start_year > current[0].start_year:
                active_map[active.educational_program_id] = (active, fos)
        return active_map

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
