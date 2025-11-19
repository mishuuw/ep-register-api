from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.department.department_repo import DepartmentRepository
from src.department.department_schema import (
    DepartmentGetSchema,
    DepartmentGetViewSchema,
    DepartmentSchema,
    DepartmentUpdateSchema,
)
from src.department.department_usecase import DepartmentUsecase
from src.models.department import DepartmentOrm


class DepartmentService:
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
        self.department_usecase = DepartmentUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.department_repo = DepartmentRepository(
            lang=lang,
            back=back,
            session=session,
        )

    async def department_delete(
        self,
        department_id: int,
    ) -> SuccessSchema:
        department = await self.common_repo.get_one(
            DepartmentOrm,
            DepartmentOrm.id == department_id,
        )
        if not department:
            raise NotFoundHttpException(name="Department")

        await self.common_repo.delete(
            DepartmentOrm,
            DepartmentOrm.id == department.id,
        )

        return SuccessSchema(detail="success")

    async def department_update(
        self, data: DepartmentUpdateSchema
    ) -> SuccessSchema:
        department = await self.common_repo.get_one(
            DepartmentOrm,
            DepartmentOrm.id == data.id,
        )
        if not department:
            raise NotFoundHttpException(name="Department")

        data_dict = data.model_dump(exclude_unset=True)
        result = await self.common_repo.update(
            DepartmentOrm(
                **data_dict,
            )
        )
        if result.id:
            return SuccessSchema(detail="success")

    async def department_add(self, data: DepartmentSchema) -> AddViewSchema:
        department = await self.common_repo.add(
            DepartmentOrm(
                code=data.code, title=data.title, title_short=data.title_short, school_id=data.school_id
            )
        )

        return AddViewSchema(
            id=department.id,
        )

    async def department_get(
        self,
    ) -> DepartmentGetViewSchema:
        departments = await self.common_repo.get_all_scalars(
            DepartmentOrm,
        )

        return DepartmentGetViewSchema(
            count=len(departments),
            result=[
                DepartmentGetSchema(
                    id=department.id,
                    code=department.code,
                    title=department.title,
                    title_short=department.title_short,
                    school_id=department.school_id,
                )
                for department in departments
            ],
        )