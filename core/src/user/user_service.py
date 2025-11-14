from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, DependencyCheckSchema, SuccessSchema
from src.models.department import DepartmentOrm
from src.models.field_of_study import FieldOfStudyOrm
from src.models.school import SchoolOrm
from src.user.user_schema import UserGetSchema, UserGetViewSchema, UserSchema, UserUpdateSchema
from src.user.user_usecase import UserUsecase
from src.user.user_repo import UserRepository
from src.models.user import UserOrm
from src.utils.common_util import timeit


class UserService:
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
        self.user_usecase = UserUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.user_repo = UserRepository(
            lang=lang,
            back=back,
            session=session,
        )

    async def user_delete(
        self,
        user_id: int,
    ) -> SuccessSchema:
        user = await self.common_repo.get_one(
            UserOrm,
            UserOrm.id == user_id,
        )
        if not user:
            raise NotFoundHttpException(
                name="User",
            )

        await self.common_repo.delete(
            UserOrm,
            UserOrm.id == user_id,
        )

        return SuccessSchema(detail="success")

    async def user_update(
        self,
        data: UserUpdateSchema,
    ) -> AddViewSchema:
        
        #check user
        user = await self.common_repo.get_one(
            UserOrm,
            UserOrm.id == data.id,
        )
        if not user:
            raise NotFoundHttpException(
                name="User",
            )
            
        #check dependencies
        dependencies = []
        if data.department_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=DepartmentOrm,
                    id=data.department_id,
                )
            )
        if data.school_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=SchoolOrm,
                    id=data.school_id,
                )
            )
        if data.field_of_study_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=FieldOfStudyOrm,
                    id=data.field_of_study_id,
                )
            )
        missing = await self.common_repo.check_dependencies(dependencies)
        if missing is not True:
            raise NotFoundHttpException(
                name=missing.__tablename__,
            )
        
        #update user
        data_dict = data.model_dump(exclude_unset=True)
        
        await self.common_repo.update(
            UserOrm(
                **data_dict
            )
        )
            
        return SuccessSchema(detail="success")

    async def user_add(
        self,
        data: UserSchema,
    ) -> AddViewSchema:
        
        dependencies = []
        if data.department_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=DepartmentOrm,
                    id=data.department_id,
                )
            )
        if data.school_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=SchoolOrm,
                    id=data.school_id,
                )
            )
        if data.field_of_study_id is not None:
            dependencies.append(
                DependencyCheckSchema(
                    table=FieldOfStudyOrm,
                    id=data.field_of_study_id,
                )
            )
        missing = await self.common_repo.check_dependencies(dependencies)
        if missing is not True:
            raise NotFoundHttpException(
                name=missing.__tablename__,
            )
        
        user = await self.common_repo.add(
            UserOrm(
                full_name=data.full_name,
                phone=data.phone,
                email=data.email,
                position=data.position,
                internal_number=data.internal_number,
                department_id=data.department_id,
                is_active=data.is_active,
                access_level=data.access_level,
                school_id=data.school_id,
                field_of_study_id=data.field_of_study_id,
            )
        )
        return AddViewSchema(
            id=user.id,
        )

    async def user_get(
        self,
    ) -> UserGetViewSchema:
        return await self.user_repo.user_get()
    