from typing import Literal, Optional, Tuple
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jwt import decode, encode
from jwt import ExpiredSignatureError, InvalidTokenError

from src.common.common_repo import CommonRepository
from src.auth.auth_repo import AuthRepository
from src.auth.auth_schema import CredentialsSchema
from src.common.common_exc import (
    InvalidHttpException,
    NotAllowedHttpException,
    NotFoundHttpException,
)
from src.common.common_schema import SuccessSchema
from src.config.settings import get_settings
from src.models.auth import AuthOrm, CredentialsOrm
from src.models.enum import AccessLevelEnum
from src.models.user import UserOrm


crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


class AuthUsecase:
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
        self.auth_repo = AuthRepository(
            lang=lang,
            back=back,
            session=session,
        )

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return crypt_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(plain_password: str) -> str:
        if plain_password is None:
            raise InvalidHttpException(name="password")

        # bcrypt only supports up to 72 bytes; enforce this explicitly
        if len(plain_password.encode("utf-8")) > 72:
            raise InvalidHttpException(name="password too long")

        return crypt_context.hash(plain_password)

    async def verify_access_token(self, token: str) -> dict:
        """Validate access JWT and return decoded payload.

        Raises InvalidHttpException on any problem.
        """
        try:
            data = decode(
                jwt=token,
                key=settings.SECRET_AUTH,
                algorithms=[settings.ALGORITHM],
            )
        except ExpiredSignatureError:
            raise InvalidHttpException(name="Bearer token expired")
        except InvalidTokenError:
            raise InvalidHttpException(name="Bearer token")

        return data

    async def create_access_token(self, user_id: int) -> str:
        now = datetime.now()
        payload = {
            "sub": user_id,
            "exp": now + timedelta(hours=1),
            "iat": now,
            "iss": settings.SERVICE,
        }
        return encode(
            payload,
            settings.SECRET_AUTH,
            algorithm=settings.ALGORITHM,
        )

    async def create_refresh_token(self, user_id: int) -> str:
        # Invalidate previous refresh tokens for this user
        await self.common_repo.delete(
            AuthOrm,
            AuthOrm.user_id == user_id,
        )

        raw_token = str(uuid4())[:72]
        await self.common_repo.add(
            AuthOrm(
                user_id=user_id,
                expires_at=datetime.now(tz=None) + timedelta(days=30),
                token_hash=crypt_context.hash(raw_token),
            )
        )
        return raw_token

    async def verify_refresh_token(self, token: str) -> Optional[int]:
        """Validate refresh token and return associated user_id or None."""
        auth_record = await self.common_repo.get_one(
            AuthOrm,
            AuthOrm.token_hash.isnot(None),
        )
        if not auth_record:
            return None

        if auth_record.expires_at < datetime.now(tz=None):
            return None

        if not crypt_context.verify(token, auth_record.token_hash):
            return None

        return auth_record.user_id

    async def authenticate_user(
        self, credentials: CredentialsSchema
    ) -> Tuple[SuccessSchema, str, str]:
        """Authenticate user and return (result, refresh_token, access_token)."""
        user = await self.common_repo.get_one(
            UserOrm,
            UserOrm.email == credentials.email,
        )
        if not user:
            raise NotFoundHttpException(name="user")

        db_credentials = await self.common_repo.get_one(
            CredentialsOrm,
            CredentialsOrm.user_id == user.id,
        )
        if not db_credentials:
            raise NotFoundHttpException(name="credentials")

        if not self.verify_password(
            plain_password=credentials.password,
            hashed_password=db_credentials.password_hash,
        ):
            raise NotAllowedHttpException(name="credentials")

        refresh_token = await self.create_refresh_token(user_id=user.id)
        access_token = await self.create_access_token(user_id=user.id)

        return SuccessSchema(detail="success"), refresh_token, access_token

    async def ensure_access_level(
        self, user_id: int, required: AccessLevelEnum
    ) -> None:
        """Ensure user has at least the required access level or raise."""
        user = await self.common_repo.get_one(
            UserOrm,
            UserOrm.id == user_id,
        )
        if not user or user.access_level.level < required.level:
            raise NotAllowedHttpException(name="access level")
