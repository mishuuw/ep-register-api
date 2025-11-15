from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.models.school import SchoolOrm
from src.school.school_repo import SchoolRepository
from src.school.school_schema import (
    SchoolGetSchema,
    SchoolGetViewSchema,
    SchoolSchema,
    SchoolUpdateSchema,
)
from src.school.school_usecase import SchoolUsecase


class SchoolService:
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
        self.school_usecase = SchoolUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.school_repo = SchoolRepository(
            lang=lang,
            back=back,
            session=session,
        )

    async def school_delete(
        self,
        school_id: int,
    ) -> SuccessSchema:
        school = await self.common_repo.get_one(
            SchoolOrm,
            SchoolOrm.id == school_id,
        )
        if not school:
            raise NotFoundHttpException(name="School")

        await self.common_repo.delete(SchoolOrm, SchoolOrm.id == school.id)
        return SuccessSchema(detail="success")

    async def school_update(
        self,
        data: SchoolUpdateSchema,
    ) -> SuccessSchema:
        school = await self.common_repo.get_one(SchoolOrm, SchoolOrm.id == data.id)
        if not school:
            raise NotFoundHttpException(name="School")

        data_dict = data.model_dump(exclude_unset=True)
        result = await self.common_repo.update(SchoolOrm(**data_dict))
        if result.id:
            return SuccessSchema(detail="success")

    async def school_add(self, data: SchoolSchema) -> AddViewSchema:
        school = await self.common_repo.add(
            SchoolOrm(
                code=data.code,
                title=data.title,
                title_short=data.title_short,
            )
        )
        return AddViewSchema(id=school.id)

    async def school_get(self) -> SchoolGetViewSchema:
        schools = await self.common_repo.get_all_scalars(SchoolOrm)

        return SchoolGetViewSchema(
            count=len(schools),
            result=[
                SchoolGetSchema(
                    id=school.id,
                    code=school.code,
                    title=school.title,
                    title_short=school.title_short,
                )
                for school in schools
            ],
        )
