from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.field_of_study.field_of_study_repo import FieldOfStudyRepository
from src.field_of_study.field_of_study_schema import (
    FieldOfStudyGetSchema,
    FieldOfStudyGetViewSchema,
    FieldOfStudySchema,
    FieldOfStudyUpdateSchema,
)
from src.field_of_study.field_of_study_usecase import FieldOfStudyUsecase
from src.models.field_of_study import FieldOfStudyOrm


class FieldOfStudyService:
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
        self.field_of_study_usecase = FieldOfStudyUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.field_of_study_repo = FieldOfStudyRepository(
            lang=lang,
            back=back,
            session=session,
        )

    async def field_of_study_delete(
        self,
        field_of_study_id: int,
    ) -> SuccessSchema:
        field_of_study = await self.common_repo.get_one(
            FieldOfStudyOrm,
            FieldOfStudyOrm.id == field_of_study_id,
        )
        if not field_of_study:
            raise NotFoundHttpException(name="Field of Study")

        await self.common_repo.delete(
            FieldOfStudyOrm,
            FieldOfStudyOrm.id == field_of_study.id,
        )

        return SuccessSchema(detail="success")

    async def field_of_study_update(
        self, data: FieldOfStudyUpdateSchema
    ) -> SuccessSchema:
        field_of_study = await self.common_repo.get_one(
            FieldOfStudyOrm,
            FieldOfStudyOrm.id == data.id,
        )
        if not field_of_study:
            raise NotFoundHttpException(name="Field of Study")

        data_dict = data.model_dump(exclude_unset=True)
        result = await self.common_repo.update(
            FieldOfStudyOrm(
                **data_dict,
            )
        )
        if result.id:
            return SuccessSchema(detail="success")

    async def field_of_study_add(self, data: FieldOfStudySchema) -> AddViewSchema:
        field_of_study = await self.common_repo.add(
            FieldOfStudyOrm(
                code=data.code, title=data.title, title_short=data.title_short
            )
        )

        return AddViewSchema(
            id=field_of_study.id,
        )

    async def field_of_study_get(
        self,
    ) -> FieldOfStudyGetViewSchema:
        fields_of_study = await self.common_repo.get_all_scalars(
            FieldOfStudyOrm,
        )

        return FieldOfStudyGetViewSchema(
            count=len(fields_of_study),
            result=[
                FieldOfStudyGetSchema(
                    id=f_o_s.id,
                    code=f_o_s.code,
                    title=f_o_s.title,
                    title_short=f_o_s.title_short,
                )
                for f_o_s in fields_of_study
            ],
        )
