import os
from enum import Enum
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Environment(Enum):
    dev: str = "dev"
    prod: str = "prod"


class DatabaseSettings(BaseSettings):
    host: str = os.environ.get("DB_HOST")
    port: str = os.environ.get("DB_PORT")
    name: str = os.environ.get("DB_NAME")
    user: str = os.environ.get("DB_USER")
    password: str = os.environ.get("DB_PASS")

    class Config:
        env_prefix = "POSTGRES_DB_"

    @property
    def async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            + f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def url(self) -> str:
        return (
            f"postgresql://{self.user}:{self.password}"
            + f"@{self.host}:{self.port}/{self.name}"
        )


class Settings(BaseSettings):
    match (os.environ.get("MODE", "dev")):
        case "prod":
            ENVIRONMENT: Environment = Environment.prod
            dotenv_path: str = os.path.join(os.path.dirname(__file__), ".env.prod")
        case _:
            ENVIRONMENT: Environment = Environment.dev
            dotenv_path: str = os.path.join(os.path.dirname(__file__), ".env.dev")

    load_dotenv(dotenv_path=dotenv_path)

    SERVICE: str = "ep-register"
    HOST: str = os.environ.get("HOST")
    MODE: str = os.environ.get("MODE", "dev")
    SECRET_AUTH: str = os.environ.get("SECRET_AUTH")
    EP_REGISTER_COOKIE_NAME: str = os.environ.get("EP_REGISTER_COOKIE_NAME")
    ALGORITHM: str = os.environ.get("ALGORITHM")
    ALLOWED_CORS_ORIGINS: set = {
        HOST,
        "127.0.0.1",
        "host.docker.internal",
        # "*",
        # "http://localhost",
        "http://localhost:8080",  # frontend dev
    }


@lru_cache(maxsize=1)
def get_settings():
    return Settings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()
