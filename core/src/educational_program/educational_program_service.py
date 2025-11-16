from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
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
    EducationalProgramActiveViewSchema,
    EducationalProgramAddSchema,
    EducationalProgramGetFilterSchema,
    EducationalProgramGetViewSchema,
    EducationalProgramHierarchyViewSchema,
)
from src.educational_program.educational_program_usecase import (
    EducationalProgramUsecase,
)
from src.models.degree import DegreeOrm
from src.models.educational_program import (
    EducationalProgramActiveOrm,
    EducationalProgramOrm,
)
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

    async def educational_program_delete(
        self,
        educational_program_id: int,
        delete_behavior: DeleteBehaviorEnum,
    ) -> SuccessSchema:
        children_ids = await self.educational_program_repo._get_all_children_ids(
            educational_program_id=educational_program_id,
        )
        if children_ids != []:
            match delete_behavior:
                case DeleteBehaviorEnum.RESTRICT:
                    raise DeletionRestrictedHttpException()
                case DeleteBehaviorEnum.CASCADE:
                    await self.common_repo.delete(
                        EducationalProgramOrm,
                        EducationalProgramOrm.id.in_(
                            children_ids + [educational_program_id]
                        ),
                    )
                case DeleteBehaviorEnum.SET_NULL:
                    await self.common_repo.delete(
                        EducationalProgramOrm,
                        EducationalProgramOrm.id == educational_program_id,
                    )
        return SuccessSchema(detail="success")

    async def educational_program_add(
        self,
        data: EducationalProgramAddSchema,
    ) -> AddViewSchema:

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

    async def educational_program_get(
        self,
    ) -> EducationalProgramGetViewSchema:
        result = await self.educational_program_repo.educational_program_get()

        return result
