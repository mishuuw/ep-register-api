from typing import Literal
from io import BytesIO

from fastapi import BackgroundTasks
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
import xlsxwriter
from src.common.common_exc import (
    AlreadyExistsHttpException,
    NotFoundHttpException,
    ShouldntBeNullHttpException,
)
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, DependencyCheckSchema, SuccessSchema
from src.educational_program.educational_program_exc import (
    DeletionRestrictedHttpException,
)
from src.educational_program.educational_program_repo import (
    EducationalProgramRepository,
)
from src.educational_program.educational_program_schema import (
    EducationalProgramActiveExportRequestSchema,
    EducationalProgramActiveViewSchema,
    EducationalProgramAddSchema,
    EducationalProgramGetFilterSchema,
    EducationalProgramGetViewSchema,
    EducationalProgramHierarchyViewSchema,
    SortOrderEnum,
    EducationalProgramUpdateSchema,
)
from src.educational_program.educational_program_usecase import (
    EducationalProgramUsecase,
)
from src.models.degree import DegreeOrm
from src.models.educational_program import (
    EducationalProgramActiveOrm,
    EducationalProgramOrm,
    EducationalProgramToPartnerOrm,
)
from src.models.educational_program_partner import EducationalProgramPartnerOrm
from src.models.enum import DeleteBehaviorEnum
from src.models.field_of_study import FieldOfStudyOrm
from src.models.school import SchoolOrm


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

    async def educational_program_update(
        self,
        data: EducationalProgramUpdateSchema,
    ) -> SuccessSchema:

        #
        # Check if provided dependencies exist
        #
        dependencies = []
        if data.field_of_study_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=FieldOfStudyOrm,
                    id=data.field_of_study_id,
                )
            )
        if data.parent_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=EducationalProgramOrm,
                    id=data.parent_id,
                )
            )
        if data.partner_ids:
            for partner_id in data.partner_ids:
                dependencies.append(
                    DependencyCheckSchema(
                        table=EducationalProgramPartnerOrm,
                        id=partner_id,
                    )
                )
        if data.school_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=SchoolOrm,
                    id=data.school_id,
                )
            )
        if data.degree_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=DegreeOrm,
                    id=data.degree_id,
                )
            )
        missing = await self.common_repo.check_dependencies(dependencies)
        if missing is not True:
            raise NotFoundHttpException(
                name=missing.__tablename__,
            )

        #
        # Filter unset data and prepare data for update
        #

        # unsafe::educational_program_schema.py:56
        data_filtered = data.model_dump(exclude_unset=True)

        is_active_provided = "is_active" in data_filtered
        if is_active_provided:
            is_active = data_filtered.pop("is_active")
        else:
            is_active = None

        field_of_study_id_provided = "field_of_study_id" in data_filtered
        if field_of_study_id_provided:
            field_of_study_id = data_filtered.pop("field_of_study_id")
        else:
            field_of_study_id = None

        start_year_provided = "start_year" in data_filtered
        if start_year_provided:
            start_year = data_filtered.pop("start_year")
        else:
            start_year = None

        end_year_provided = "end_year" in data_filtered
        if end_year_provided:
            end_year = data_filtered.pop("end_year")
        else:
            end_year = None

        partner_ids_provided = "partner_ids" in data_filtered
        if partner_ids_provided:
            partner_ids = data_filtered.pop("partner_ids")
        else:
            partner_ids = None

        # Update object in database
        upd_obj = await self.common_repo.update(EducationalProgramOrm(**data_filtered))

        # If needed, update partner links
        if partner_ids_provided:
            await self.common_repo.delete(
                EducationalProgramToPartnerOrm,
                EducationalProgramToPartnerOrm.educational_program_id == upd_obj.id,
            )
            if partner_ids:
                await self.common_repo.add_all(
                    [
                        EducationalProgramToPartnerOrm(
                            educational_program_id=upd_obj.id,
                            partner_id=partner_id,
                        )
                        for partner_id in partner_ids
                    ]
                )

        #
        # Handle active educational program entities
        #

        active = await self.common_repo.get_one(
            EducationalProgramActiveOrm,
            EducationalProgramActiveOrm.educational_program_id == upd_obj.id,
        )

        target_field_of_study_id = (
            field_of_study_id
            if field_of_study_id_provided
            else (active.field_of_study_id if active is not None else None)
        )
        target_start_year = (
            start_year
            if start_year_provided
            else (active.start_year if active is not None else None)
        )
        target_end_year = (
            end_year
            if end_year_provided
            else (active.end_year if active is not None else None)
        )

        active_fields_supplied = (
            field_of_study_id_provided or start_year_provided or end_year_provided
        )
        should_validate_active_fields = is_active is True or active_fields_supplied

        if should_validate_active_fields:
            missing_fields = {
                name
                for name, value in {
                    "start_year": target_start_year,
                    "end_year": target_end_year,
                    "field_of_study_id": target_field_of_study_id,
                }.items()
                if value is None
            }
            if missing_fields:
                raise ShouldntBeNullHttpException(
                    name=f"One of: {', '.join(sorted(missing_fields))}"
                )

        should_have_active_after_update = is_active is True or (
            is_active is None and active is not None
        )

        if (
            should_have_active_after_update
            and target_field_of_study_id
            and target_start_year
            and target_end_year
        ):
            check = await self.common_repo.get_one(
                EducationalProgramActiveOrm,
                and_(
                    EducationalProgramActiveOrm.field_of_study_id
                    == target_field_of_study_id,
                    EducationalProgramActiveOrm.start_year == target_start_year,
                    EducationalProgramActiveOrm.end_year == target_end_year,
                ),
            )
            if check is not None and check.educational_program_id != upd_obj.id:
                raise AlreadyExistsHttpException(
                    name="EducationalProgramActive",
                )

        if active is not None:
            if is_active is False:
                await self.common_repo.delete(
                    EducationalProgramActiveOrm,
                    EducationalProgramActiveOrm.educational_program_id == upd_obj.id,
                )
            elif active_fields_supplied and should_have_active_after_update:
                await self.common_repo.update(
                    EducationalProgramActiveOrm(
                        id=active.id,
                        educational_program_id=upd_obj.id,
                        field_of_study_id=target_field_of_study_id,
                        start_year=target_start_year,
                        end_year=target_end_year,
                    )
                )
        if active is None and is_active is True:
            await self.common_repo.add(
                EducationalProgramActiveOrm(
                    educational_program_id=upd_obj.id,
                    field_of_study_id=target_field_of_study_id,
                    start_year=target_start_year,
                    end_year=target_end_year,
                )
            )

        return SuccessSchema(detail="success")

    async def educational_program_delete(
        self,
        educational_program_id: int,
        delete_behavior: DeleteBehaviorEnum,
    ) -> SuccessSchema:
        # get all descendants (recursive)
        descendants = await self.educational_program_repo._get_all_children_ids(
            educational_program_id=educational_program_id,
        )
        if descendants:
            match delete_behavior:
                case DeleteBehaviorEnum.RESTRICT:
                    raise DeletionRestrictedHttpException()
                case DeleteBehaviorEnum.CASCADE:
                    # delete all descendants
                    await self.common_repo.delete(
                        EducationalProgramOrm,
                        EducationalProgramOrm.id.in_(
                            descendants + [educational_program_id]
                        ),
                    )
                    return SuccessSchema(detail="success")
                case DeleteBehaviorEnum.SET_NULL:
                    # set NULL only for immediate children
                    immediate_children = (
                        await self.educational_program_repo._get_immediate_children_ids(
                            educational_program_id=educational_program_id
                        )
                    )
                    if immediate_children:
                        await self.common_repo.update_stmt(
                            EducationalProgramOrm,
                            EducationalProgramOrm.id.in_(immediate_children),
                            {"parent_id": None},
                        )
        await self.common_repo.delete(
            EducationalProgramOrm,
            EducationalProgramOrm.id == educational_program_id,
        )
        return SuccessSchema(detail="success")

    async def educational_program_add(
        self,
        data: EducationalProgramAddSchema,
    ) -> AddViewSchema:

        unset_keys = set(EducationalProgramAddSchema.model_fields.keys()) - set(
            data.model_dump(exclude_unset=True).keys()
        )
        if data.parent_id is not None:
            parent_row = (
                await self.session.execute(
                    select(EducationalProgramOrm, EducationalProgramActiveOrm)
                    .where(EducationalProgramOrm.id == data.parent_id)
                    .outerjoin(
                        EducationalProgramActiveOrm,
                        EducationalProgramActiveOrm.educational_program_id
                        == EducationalProgramOrm.id,
                    )
                )
            ).one_or_none()

            # Merge missing fields from parent educational / active rows into data
            if parent_row is not None:
                parent_educational, parent_active = parent_row[0], parent_row[1]
                for key in unset_keys:
                    if (
                        parent_educational is not None
                        and getattr(parent_educational, key, None) is not None
                    ):
                        setattr(data, key, getattr(parent_educational, key))
                        continue
                    if (
                        parent_active is not None
                        and getattr(parent_active, key, None) is not None
                    ):
                        setattr(data, key, getattr(parent_active, key))
                        continue

        if data.is_active:
            missing_fields = {
                name
                for name, value in {
                    "start_year": data.start_year,
                    "end_year": data.end_year,
                    "field_of_study_id": data.field_of_study_id,
                }.items()
                if value is None
            }
            if missing_fields:
                raise ShouldntBeNullHttpException(
                    name=f"One of: {', '.join(sorted(missing_fields))}"
                )

            check = await self.common_repo.get_one(
                EducationalProgramActiveOrm,
                and_(
                    EducationalProgramActiveOrm.field_of_study_id
                    == data.field_of_study_id,
                    EducationalProgramActiveOrm.start_year == data.start_year,
                    EducationalProgramActiveOrm.end_year == data.end_year,
                ),
            )
            if check is not None:
                raise AlreadyExistsHttpException(
                    name="EducationalProgramActive",
                )

        dependencies = []
        if data.partner_ids:
            for partner_id in data.partner_ids:
                dependencies.append(
                    DependencyCheckSchema(
                        table=EducationalProgramPartnerOrm,
                        id=partner_id,
                    )
                )
        if data.field_of_study_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=FieldOfStudyOrm,
                    id=data.field_of_study_id,
                )
            )
        if data.parent_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=EducationalProgramOrm,
                    id=data.parent_id,
                )
            )
        if data.school_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=SchoolOrm,
                    id=data.school_id,
                )
            )
        if data.degree_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=DegreeOrm,
                    id=data.degree_id,
                )
            )
        missing = await self.common_repo.check_dependencies(dependencies)
        if missing is not True:
            raise NotFoundHttpException(
                name=missing.__tablename__,
            )

        created = await self.common_repo.add(
            EducationalProgramOrm(
                title=data.title,
                title_short=data.title_short,
                parent_id=data.parent_id,
                school_id=data.school_id,
                degree_id=data.degree_id,
                network_form=data.network_form,
                educational_form=data.educational_form,
                educational_standard_type=data.educational_standard_type,
                language=data.language,
                language_hours=data.language_hours,
                standard_duration_months=data.standard_duration_months,
                poa_accreditation_company=data.poa_accreditation_company,
                poa_accreditation_expiry=data.poa_accreditation_expiry,
                state_accreditation_expiry=data.state_accreditation_expiry,
                description=data.description,
            )
        )

        if data.partner_ids != []:
            await self.common_repo.add_all(
                [
                    EducationalProgramToPartnerOrm(
                        educational_program_id=created.id,
                        partner_id=partner_id,
                    )
                    for partner_id in data.partner_ids
                ]
            )
        if data.is_active:
            await self.common_repo.add(
                EducationalProgramActiveOrm(
                    educational_program_id=created.id,
                    field_of_study_id=data.field_of_study_id,
                    start_year=data.start_year,
                    end_year=data.end_year,
                )
            )

        return AddViewSchema(id=created.id)

    async def educational_program_hierarchy(
        self,
        educational_program_id: int,
    ) -> EducationalProgramHierarchyViewSchema:
        return await self.educational_program_repo.educational_program_hierarchy(
            educational_program_id=educational_program_id,
        )

    async def educational_program_active_get(
        self,
        filter: EducationalProgramGetFilterSchema,
    ) -> EducationalProgramActiveViewSchema:
        result = await self.educational_program_repo.educational_program_active_get(
            filter=filter,
        )

        return result

    @staticmethod
    def _value_to_sortable(value):
        if value is None:
            return None
        if hasattr(value, "value"):
            return str(value.value).lower()
        if isinstance(value, list):
            return ", ".join(str(v) for v in value).lower()
        if isinstance(value, str):
            return value.lower()
        return value

    @staticmethod
    def _matches_membership(value, expected: list) -> bool:
        if not expected:
            return True
        if value is None:
            return False
        comparable_value = value.value if hasattr(value, "value") else value
        return comparable_value in expected

    @staticmethod
    def _matches_text_membership(value, expected: list[str]) -> bool:
        if not expected:
            return True
        if value is None:
            return False
        expected_set = {str(item).lower() for item in expected}
        return str(value).lower() in expected_set

    @staticmethod
    def _matches_partner_membership(value: list[str], expected: list[str]) -> bool:
        if not expected:
            return True
        if not value:
            return False
        current = {str(item).lower() for item in value}
        return any(str(item).lower() in current for item in expected)

    @staticmethod
    def _row_search_blob(row) -> str:
        parts = []
        for key, value in row.model_dump().items():
            if key == "tags":
                if isinstance(value, dict):
                    for tag_name, tag_data in value.items():
                        parts.append(str(tag_name))
                        if isinstance(tag_data, dict):
                            parts.append(str(tag_data.get("value", "")))
                continue
            if isinstance(value, list):
                parts.append(" ".join(str(item) for item in value))
            elif value is not None:
                parts.append(str(value.value) if hasattr(value, "value") else str(value))
        return " ".join(parts).lower()

    def _filter_active_rows(
        self,
        rows,
        payload: EducationalProgramActiveExportRequestSchema,
    ):
        filter_by = payload.filter_by
        expected = {
            "id_in": filter_by.id_in or [],
            "title_in": filter_by.title_in or [],
            "title_short_in": filter_by.title_short_in or [],
            "degree_title_in": filter_by.degree_title_in or [],
            "school_title_in": filter_by.school_title_in or [],
            "school_code_in": filter_by.school_code_in or [],
            "partner_title_in": filter_by.partner_title_in or [],
            "field_of_study_title_in": filter_by.field_of_study_title_in or [],
            "field_of_study_code_in": filter_by.field_of_study_code_in or [],
            "start_year_in": filter_by.start_year_in or [],
            "end_year_in": filter_by.end_year_in or [],
            "network_form_in": [item.value for item in (filter_by.network_form_in or [])],
            "educational_form_in": [
                item.value for item in (filter_by.educational_form_in or [])
            ],
            "educational_standard_type_in": [
                item.value for item in (filter_by.educational_standard_type_in or [])
            ],
            "language_in": [item.value for item in (filter_by.language_in or [])],
            "language_hours_in": filter_by.language_hours_in or [],
            "standard_duration_months_in": filter_by.standard_duration_months_in or [],
            "poa_accreditation_company_in": filter_by.poa_accreditation_company_in or [],
        }

        search_text = (filter_by.search or "").strip().lower()
        description_contains = (filter_by.description_contains or "").strip().lower()

        output = []
        for row in rows:
            if not self._matches_membership(row.id, expected["id_in"]):
                continue
            if not self._matches_text_membership(row.title, expected["title_in"]):
                continue
            if not self._matches_text_membership(
                row.title_short, expected["title_short_in"]
            ):
                continue
            if not self._matches_text_membership(
                row.degree_title, expected["degree_title_in"]
            ):
                continue
            if not self._matches_text_membership(
                row.school_title, expected["school_title_in"]
            ):
                continue
            if not self._matches_text_membership(
                row.school_code, expected["school_code_in"]
            ):
                continue
            if not self._matches_partner_membership(
                row.partner_titles, expected["partner_title_in"]
            ):
                continue
            if not self._matches_text_membership(
                row.field_of_study_title, expected["field_of_study_title_in"]
            ):
                continue
            if not self._matches_text_membership(
                row.field_of_study_code, expected["field_of_study_code_in"]
            ):
                continue
            if not self._matches_membership(row.start_year, expected["start_year_in"]):
                continue
            if not self._matches_membership(row.end_year, expected["end_year_in"]):
                continue
            if not self._matches_membership(
                row.network_form, expected["network_form_in"]
            ):
                continue
            if not self._matches_membership(
                row.educational_form, expected["educational_form_in"]
            ):
                continue
            if not self._matches_membership(
                row.educational_standard_type,
                expected["educational_standard_type_in"],
            ):
                continue
            if not self._matches_membership(row.language, expected["language_in"]):
                continue
            if not self._matches_membership(
                row.language_hours, expected["language_hours_in"]
            ):
                continue
            if not self._matches_membership(
                row.standard_duration_months,
                expected["standard_duration_months_in"],
            ):
                continue
            if not self._matches_text_membership(
                row.poa_accreditation_company,
                expected["poa_accreditation_company_in"],
            ):
                continue

            if (
                filter_by.poa_accreditation_expiry_from is not None
                and (
                    row.poa_accreditation_expiry is None
                    or row.poa_accreditation_expiry
                    < filter_by.poa_accreditation_expiry_from
                )
            ):
                continue
            if (
                filter_by.poa_accreditation_expiry_to is not None
                and (
                    row.poa_accreditation_expiry is None
                    or row.poa_accreditation_expiry > filter_by.poa_accreditation_expiry_to
                )
            ):
                continue
            if (
                filter_by.state_accreditation_expiry_from is not None
                and (
                    row.state_accreditation_expiry is None
                    or row.state_accreditation_expiry
                    < filter_by.state_accreditation_expiry_from
                )
            ):
                continue
            if (
                filter_by.state_accreditation_expiry_to is not None
                and (
                    row.state_accreditation_expiry is None
                    or row.state_accreditation_expiry
                    > filter_by.state_accreditation_expiry_to
                )
            ):
                continue
            if description_contains and (
                row.description is None
                or description_contains not in str(row.description).lower()
            ):
                continue
            if search_text and search_text not in self._row_search_blob(row):
                continue

            output.append(row)

        return output

    def _sort_active_rows(self, rows, payload: EducationalProgramActiveExportRequestSchema):
        sort_key = payload.sort_by.value
        reverse = payload.sort_order == SortOrderEnum.DESC

        def key_func(row):
            raw = getattr(row, sort_key)
            normalized = self._value_to_sortable(raw)
            return (normalized is None, normalized)

        return sorted(rows, key=key_func, reverse=reverse)

    @staticmethod
    def _row_to_excel(row):
        return {
            "id": row.id,
            "title": row.title,
            "title_short": row.title_short,
            "degree_title": row.degree_title,
            "school_title": row.school_title,
            "school_code": row.school_code,
            "partner_titles": ", ".join(row.partner_titles or []),
            "field_of_study_title": row.field_of_study_title,
            "field_of_study_code": row.field_of_study_code,
            "start_year": row.start_year,
            "end_year": row.end_year,
            "network_form": (
                row.network_form.value if hasattr(row.network_form, "value") else row.network_form
            ),
            "educational_form": (
                row.educational_form.value
                if hasattr(row.educational_form, "value")
                else row.educational_form
            ),
            "educational_standard_type": (
                row.educational_standard_type.value
                if hasattr(row.educational_standard_type, "value")
                else row.educational_standard_type
            ),
            "language": row.language.value if hasattr(row.language, "value") else row.language,
            "language_hours": row.language_hours,
            "standard_duration_months": row.standard_duration_months,
            "poa_accreditation_company": row.poa_accreditation_company,
            "poa_accreditation_expiry": row.poa_accreditation_expiry,
            "state_accreditation_expiry": row.state_accreditation_expiry,
            "description": row.description,
            "tags": ", ".join(
                [
                    f"{name}:{meta.get('value')}"
                    for name, meta in (row.tags or {}).items()
                ]
            ),
        }

    def _render_excel(self, rows) -> bytes:
        workbook_stream = BytesIO()
        workbook = xlsxwriter.Workbook(workbook_stream, {"in_memory": True})
        worksheet = workbook.add_worksheet("Active Programs")
        header_format = workbook.add_format({"bold": True, "bg_color": "#F2F2F2"})
        date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})

        headers = [
            "id",
            "title",
            "title_short",
            "degree_title",
            "school_title",
            "school_code",
            "partner_titles",
            "field_of_study_title",
            "field_of_study_code",
            "start_year",
            "end_year",
            "network_form",
            "educational_form",
            "educational_standard_type",
            "language",
            "language_hours",
            "standard_duration_months",
            "poa_accreditation_company",
            "poa_accreditation_expiry",
            "state_accreditation_expiry",
            "description",
            "tags",
        ]

        for col_idx, header in enumerate(headers):
            worksheet.write(0, col_idx, header, header_format)

        for row_idx, row in enumerate(rows, start=1):
            data = self._row_to_excel(row)
            for col_idx, header in enumerate(headers):
                value = data[header]
                if header in {
                    "poa_accreditation_expiry",
                    "state_accreditation_expiry",
                } and value is not None:
                    worksheet.write_datetime(row_idx, col_idx, value, date_format)
                else:
                    worksheet.write(row_idx, col_idx, value)

        worksheet.autofilter(0, 0, max(len(rows), 1), len(headers) - 1)
        worksheet.freeze_panes(1, 0)
        worksheet.set_column(0, len(headers) - 1, 20)
        workbook.close()
        workbook_stream.seek(0)
        return workbook_stream.read()

    async def educational_program_active_export_excel(
        self,
        payload: EducationalProgramActiveExportRequestSchema,
    ) -> bytes:
        result = await self.educational_program_repo.educational_program_active_get(
            filter=payload.base_filter,
        )
        filtered_rows = self._filter_active_rows(result.result, payload)
        sorted_rows = self._sort_active_rows(filtered_rows, payload)
        return self._render_excel(sorted_rows)

    async def educational_program_get(
        self,
    ) -> EducationalProgramGetViewSchema:
        result = await self.educational_program_repo.educational_program_get()

        return result
