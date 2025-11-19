import fastapi_swagger_dark as fsd
from fastapi import APIRouter
from src.config.settings import Environment, get_settings
from src.degree.degree_controller import degree_router
from src.department.department_controller import department_router
from src.educational_program.educational_program_controller import (
    educational_program_router,
)
from src.educational_program_partner.educational_program_partner_controller import (
    educational_program_partner_router,
)
from src.field_of_study.field_of_study_controller import field_of_study_router
from src.school.school_controller import school_router
from src.user.user_controller import user_router
from src.auth.auth_controller import auth_router

api_router = APIRouter()

settings = get_settings()

if settings.ENVIRONMENT == Environment.dev:
    fsd.install(api_router)

api_router.include_router(educational_program_router, prefix="/educational_program")
api_router.include_router(
    educational_program_partner_router, prefix="/educational_program_partner"
)
api_router.include_router(department_router, prefix="/department")
api_router.include_router(degree_router, prefix="/degree")
api_router.include_router(field_of_study_router, prefix="/field_of_study")
api_router.include_router(school_router, prefix="/school")
api_router.include_router(user_router, prefix="/user")
api_router.include_router(auth_router, prefix="/auth")


@api_router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
