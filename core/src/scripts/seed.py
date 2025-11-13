import asyncio
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.db_util import get_session
from src.models.school import SchoolOrm
from src.models.department import DepartmentOrm
from src.models.degree import DegreeOrm
from src.models.field_of_study import FieldOfStudyOrm
from src.models.user import UserOrm
from src.models.enum import AccessLevelEnum


async def get_one(session: AsyncSession, model, **by):
    return await session.scalar(select(model).filter_by(**by))


async def upsert(
    session: AsyncSession,
    model,
    where: dict,
    values: dict,
):
    row = await get_one(session, model, **where)
    if row is None:
        row = model(**{**where, **values})
        session.add(row)
        return row, True
    # update existing with provided values (idempotent)
    for k, v in values.items():
        setattr(row, k, v)
    return row, False


async def seed(session: AsyncSession) -> None:
    # Schools
    school, _ = await upsert(
        session,
        SchoolOrm,
        where={"code": "9"},
        values={"title": "Институт математики и компьютерных технологий", "title_short": "ИМКТ"},
    )

    # Departments
    dept, _ = await upsert(
        session,
        DepartmentOrm,
        where={"title": "Департамент математического и компьютерного моделирования"},
        values={},
    )

    # Degrees
    await upsert(
        session,
        DegreeOrm,
        where={"title": "Бакалавр"},
        values={},
    )

    await upsert(
        session,
        DegreeOrm,
        where={"title": "Магистр"},
        values={},
    )

    # Fields of study
    await upsert(
        session,
        FieldOfStudyOrm,
        where={"code": "09.03.03"},
        values={"title": "Прикладная информатика", "title_short": "ПИ"},
    )

    # Users (dummy)
    await upsert(
        session,
        UserOrm,
        where={"email": "admin@example.com"},
        values={
            "phone": "+1000000000",
            "position": "Директор",
            "full_name": "Админов админ админович",
            "internal_number": "1001",
            "access_level": AccessLevelEnum.admin,
            "department_id": dept.id,
            "is_active": True,
        },
    )

    await upsert(
        session,
        UserOrm,
        where={"email": "manager@example.com"},
        values={
            "phone": "+1000000001",
            "position": "РОП",
            "full_name": "Ропов роп ропович",
            "internal_number": "1002",
            "access_level": AccessLevelEnum.manager,
            "school_id": school.id,
            "department_id": dept.id,
            "is_active": True,
        },
    )


async def main() -> None:
    async with get_session() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
