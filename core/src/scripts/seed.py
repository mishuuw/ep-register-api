import asyncio

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.degree import DegreeOrm
from src.models.department import DepartmentOrm
from src.models.enum import (
    AccessLevelEnum,
    EducationalFormEnum,
    EducationalProgramLanguageTypeEnum,
    EducationalProgramPartnerEnum,
    EducationalStandartEnum,
    NetworkFormEnum,
)
from src.models.educational_program import (
    EducationalProgramActiveOrm,
    EducationalProgramOrm,
)
from src.models.educational_program_partner import EducationalProgramPartnerOrm
from src.models.field_of_study import FieldOfStudyOrm
from src.models.school import SchoolOrm
from src.models.user import UserOrm
from src.utils.db_util import get_session


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
        values={
            "title": "Институт математики и компьютерных технологий",
            "title_short": "ИМКТ",
        },
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
    f_o_s, _ = await upsert(
        session,
        FieldOfStudyOrm,
        where={"code": "09.03.03"},
        values={"title": "Прикладная информатика", "title_short": "ПИ"},
    )

    # Educational program partners
    partner_oo, _ = await upsert(
        session,
        EducationalProgramPartnerOrm,
        where={"title": "Партнер ОО"},
        values={
            "partner_type": (EducationalProgramPartnerEnum.OO),
            "hours": 120,
        },
    )

    # Educational programs
    edu_program, _ = await upsert(
        session,
        EducationalProgramOrm,
        where={"title": "Прикладная информатика (основная программа)"},
        values={
            "title_short": "ПИ",
            "school_id": school.id,
            "degree_id": (await get_one(session, DegreeOrm, title="Бакалавр")).id,
            "partner_id": partner_oo.id,
            "network_form": NetworkFormEnum.FEFU_BASIC,
            "educational_form": EducationalFormEnum.OFFLINE,
            "educational_standart_type": EducationalStandartEnum.FGOS_VO_3_PLUS,
            "language": EducationalProgramLanguageTypeEnum.RUSSIAN,
            "language_hours": 72,
            "curriculum_number": "ПИ-09.03.03-2025",
            "standart_duration_months": 48,
            "poa_accreditation_expiry": date(2030, 6, 30),
            "state_accreditation_expiry": date(2032, 12, 31),
            "description": """Базовая образовательная программа по направлению
            Прикладная информатика.""",
        },
    )

    # Ensure program is flushed so it has an ID before active period
    await session.flush()

    # Educational program active period
    await upsert(
        session,
        EducationalProgramActiveOrm,
        where={
            "educational_program_id": edu_program.id,
            "field_of_study_id": f_o_s.id,
            "start_year": 2025,
            "end_year": 2029,
        },
        values={},
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
            "field_of_study_id": f_o_s.id,
            "is_active": True,
        },
    )


async def main() -> None:
    async with get_session() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
