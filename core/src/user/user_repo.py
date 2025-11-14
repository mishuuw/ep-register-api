from typing import List, Literal

from fastapi import BackgroundTasks
from sqlalchemy import and_, case, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.config.settings import get_settings
from src.models.department import DepartmentOrm
from src.models.field_of_study import FieldOfStudyOrm
from src.models.school import SchoolOrm
from src.models.user import UserOrm
from src.user.user_schema import UserGetSchema, UserGetViewSchema

settings = get_settings()


class UserRepository:
    def __init__(
        self,
        lang: Literal["ru", "en"],
        back: BackgroundTasks,
        session: AsyncSession,
    ):
        self.lang = lang
        self.back = back
        self.session = session

    async def user_get(self) -> List[UserGetSchema]:
        result = (await self.session.execute(
            select(
                UserOrm,
                DepartmentOrm,
                SchoolOrm,
                FieldOfStudyOrm,
            )
            .outerjoin(
                DepartmentOrm,
                UserOrm.department_id == DepartmentOrm.id
            )
            .outerjoin(
                SchoolOrm,
                UserOrm.school_id == SchoolOrm.id
            )
            .outerjoin(
                FieldOfStudyOrm,
                UserOrm.field_of_study_id == FieldOfStudyOrm.id
            )
        )).all()

        return UserGetViewSchema(
            count=len(result),
            result=[
                UserGetSchema(
                    id=user.id,
                    full_name=user.full_name,
                    phone=user.phone,
                    email=user.email,
                    position=user.position,
                    internal_number=user.internal_number,
                    department_title=department.title if department is not None else None,
                    is_active=user.is_active,
                    field_of_study=(field_of_study.code + field_of_study.title_short.lower()) if field_of_study is not None and field_of_study.code and field_of_study.title_short else None,
                    access_level=user.access_level,
                    school_title=school.title if school is not None else None,
                ) for user, department, school, field_of_study in result
            ],
        )