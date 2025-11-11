import fastapi_swagger_dark as fsd
from fastapi import APIRouter
from src.config.settings import Environment, get_settings
from src.feature.feature_controller import feature_router

api_router = APIRouter()

settings = get_settings()

if settings.ENVIRONMENT == Environment.dev:
    fsd.install(api_router)

api_router.include_router(
    feature_router, prefix="/feature"
)

@api_router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
