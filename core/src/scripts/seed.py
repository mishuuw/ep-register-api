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
    EducationalstandardEnum,
    NetworkFormEnum,
    TagTypeEnum,
)
from src.models.educational_program import (
    EducationalProgramActiveOrm,
    EducationalProgramOrm,
    EducationalProgramToPartnerOrm,
)
from src.models.educational_program_partner import EducationalProgramPartnerOrm
from src.models.field_of_study import FieldOfStudyOrm
from src.models.school import SchoolOrm
from src.models.user import UserOrm
from src.models.tag import (TagOrm, TagToEducationalProgramOrm)
from src.models.auth import CredentialsOrm
from src.auth.auth_usecase import AuthUsecase
from src.utils.db_util import get_session


async def get_one(session: AsyncSession, model, **by):
    result = await session.execute(select(model).filter_by(**by))
    return result.scalars().first()


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

    bachelor_degree = await get_one(session, DegreeOrm, title="Бакалавр")

    # Fields of study for each program
    f_o_s_base, _ = await upsert(
        session,
        FieldOfStudyOrm,
        where={"code": "09.03.01"},
        values={"title": "Информатика и вычислительная техника", "title_short": "ИВТ"},
    )

    f_o_s_core, _ = await upsert(
        session,
        FieldOfStudyOrm,
        where={"code": "09.03.02"},
        values={"title": "Информационные системы и технологии", "title_short": "ИСТ"},
    )

    f_o_s_advanced, _ = await upsert(
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

    await session.flush()

    # Tags
    tag_ege, _ = await upsert(
        session,
        TagOrm,
        where={"name": "Балл ЕГЭ"},
        values={
            "type": TagTypeEnum.NUMBER,
            "number_value": 231,
            "text_value": None,
            "boolean_value": None,
        },
    )

    tag_project, _ = await upsert(
        session,
        TagOrm,
        where={"name": "Национальный проект"},
        values={
            "type": TagTypeEnum.BOOLEAN,
            "boolean_value": True,
            "number_value": None,
            "text_value": None,
        },
    )

    tag_simple, _ = await upsert(
        session,
        TagOrm,
        where={"name": "Норм"},
        values={
            "type": TagTypeEnum.SIMPLE,
            "boolean_value": None,
            "number_value": None,
            "text_value": None,
        },
    )

    tag_text, _ = await upsert(
        session,
        TagOrm,
        where={"name": "Руководитель"},
        values={
            "type": TagTypeEnum.TEXT,
            "text_value": "Василий Пупкин",
            "boolean_value": None,
            "number_value": None,
        },
    )

    # Educational programs linked via parent-child relationship
    base_program, _ = await upsert(
        session,
        EducationalProgramOrm,
        where={"title": "Цифровые системы: фундамент"},
        values={
            "title_short": "CSF",
            "school_id": school.id,
            "degree_id": bachelor_degree.id,
            "network_form": NetworkFormEnum.FEFU_BASIC,
            "educational_form": EducationalFormEnum.OFFLINE,
            "educational_standard_type": EducationalstandardEnum.FGOS_VO_3_PLUS,
            "language": EducationalProgramLanguageTypeEnum.RUSSIAN,
            "language_hours": 64,
            "standard_duration_months": 48,
            "poa_accreditation_company": "Аккредитационная компания ООО",
            "poa_accreditation_expiry": date(2030, 6, 30),
            "state_accreditation_expiry": date(2032, 12, 31),
            "description": "Фундаментальная подготовка по цифровым системам.",
        },
    )

    await session.flush()

    core_program, _ = await upsert(
        session,
        EducationalProgramOrm,
        where={"title": "Цифровые системы: ядро продуктов"},
        values={
            "title_short": "CSC",
            "parent_id": base_program.id,
            "school_id": school.id,
            "degree_id": bachelor_degree.id,
            "network_form": NetworkFormEnum.FEFU_BASIC,
            "educational_form": EducationalFormEnum.OFFLINE,
            "educational_standard_type": EducationalstandardEnum.FGOS_VO_3_PLUS,
            "language": EducationalProgramLanguageTypeEnum.RUSSIAN,
            "language_hours": 72,
            "standard_duration_months": 48,
            "poa_accreditation_company": "Аккредитационная компания ООО",
            "poa_accreditation_expiry": date(2030, 6, 30),
            "state_accreditation_expiry": date(2032, 12, 31),
            "description": "Программа ядра цифровых продуктов с упором на практику.",
        },
    )

    await session.flush()

    advanced_program, _ = await upsert(
        session,
        EducationalProgramOrm,
        where={"title": "Цифровые системы: управление и рост"},
        values={
            "title_short": "CSM",
            "parent_id": core_program.id,
            "school_id": school.id,
            "degree_id": bachelor_degree.id,
            "network_form": NetworkFormEnum.FEFU_BASIC,
            "educational_form": EducationalFormEnum.OFFLINE,
            "educational_standard_type": EducationalstandardEnum.FGOS_VO_3_PLUS,
            "language": EducationalProgramLanguageTypeEnum.RUSSIAN,
            "language_hours": 68,
            "standard_duration_months": 48,
            "poa_accreditation_company": "Аккредитационная компания ООО",
            "poa_accreditation_expiry": date(2030, 6, 30),
            "state_accreditation_expiry": date(2032, 12, 31),
            "description": "Продвинутая траектория по управлению цифровыми решениями.",
        },
    )

    await session.flush()

    # Link educational programs to a partner via junction table
    for program in (base_program, core_program, advanced_program):
        await upsert(
            session,
            EducationalProgramToPartnerOrm,
            where={
                "educational_program_id": program.id,
                "partner_id": partner_oo.id,
            },
            values={},
        )

    # Link educational programs to tags via junction table
    for program, tag in (
        (base_program, tag_ege),
        (core_program, tag_project),
        (advanced_program, tag_simple),
        (advanced_program, tag_text),
    ):
        await upsert(
            session,
            TagToEducationalProgramOrm,
            where={
                "educational_program_id": program.id,
                "tag_id": tag.id,
            },
            values={},
        )
    
    # Educational program active periods (make all programs active with different FoS)
    await upsert(
        session,
        EducationalProgramActiveOrm,
        where={
            "educational_program_id": base_program.id,
            "field_of_study_id": f_o_s_base.id,
            "start_year": 2025,
            "end_year": 2029,
        },
        values={},
    )

    await upsert(
        session,
        EducationalProgramActiveOrm,
        where={
            "educational_program_id": core_program.id,
            "field_of_study_id": f_o_s_core.id,
            "start_year": 2025,
            "end_year": 2029,
        },
        values={},
    )

    await upsert(
        session,
        EducationalProgramActiveOrm,
        where={
            "educational_program_id": advanced_program.id,
            "field_of_study_id": f_o_s_advanced.id,
            "start_year": 2025,
            "end_year": 2029,
        },
        values={},
    )

    # Users (dummy) with credentials
    admin_user, _ = await upsert(
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

    manager_user, _ = await upsert(
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
            "field_of_study_id": f_o_s_core.id,
            "is_active": True,
        },
    )

    # Seed credentials for demo users using AuthUsecase hashing
    auth_usecase = AuthUsecase(session=session, back=None, lang="en")

    for user, password in (
        (admin_user, "admin"),
        (manager_user, "manager"),
    ):
        if user is None:
            continue
        password_hash = auth_usecase.hash_password(password)
        await upsert(
            session,
            CredentialsOrm,
            where={"user_id": user.id},
            values={"password_hash": password_hash},
        )


async def main() -> None:
    async with get_session() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
