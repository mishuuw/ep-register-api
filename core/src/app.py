from contextlib import asynccontextmanager

import src.config.exception_config as exh
import ujson
from fastapi import FastAPI, HTTPException
from fastapi.datastructures import Default
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import UJSONResponse
from src.config.settings import Environment, get_settings
from src.utils import db_util
from src.v1 import api_router as v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.json_encoder = ujson

    yield

    await db_util.shutdown()


app = FastAPI(
    title=settings.SERVICE,
    lifespan=lifespan,
    openapi_url=("" if settings.ENVIRONMENT == Environment.prod else "/dev")
    + "/api/v1/openapi.json",
    debug=settings.ENVIRONMENT != Environment.prod,
    default_response_class=Default(UJSONResponse),
)

if settings.ENVIRONMENT == Environment.prod:
    app.docs_url = ""
    app.redoc_url = ""
    app.openapi_url = ""
    prefix = ""

else:
    prefix = "/dev"


def custom_openapi():
    openapi_schema = get_openapi(
        title=settings.SERVICE,
        version="1.0.0",
        description="",
        routes=app.routes,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "CookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "ep-register-token",
        },
    }

    openapi_schema["security"] = [{"CookieAuth": []}, {"Bearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    HTTPException,
    exh.http_exception_handler,
)

app.include_router(v1_router, prefix=prefix + "/api/v1")
