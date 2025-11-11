from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.feature.feature_schema import (
    FeatureGetSchema,
    FeatureGetViewSchema,
    FeatureAddViewSchema,
    FeatureAddSchema
)
from src.feature.feature_service import FeatureService
from src.common.common_exc import NotAllowedHttpException
from src.common.token_service import token_service
from src.config.settings import get_settings
from src.user.user_schema import UserSchema
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

feature_router = APIRouter()
settings = get_settings()


@cbv(feature_router)
class FeatureController:
    def __init__(
        self,
        back: BackgroundTasks,
        session: AsyncSession = Depends(get_session_obj),
        lang: Literal["ru", "en"] = Query(
            default="ru",
            description="Language code",
        ),
    ):
        self.lang = lang
        self.back = back
        self.session = session

        self.feature_service = FeatureService(
            lang=lang,
            back=back,
            session=session,
        )

    @feature_router.get("/get", tags=["feature"])
    @try_rollback
    async def feature_get(
        self,
        data: FeatureGetSchema = Depends(),
        _: UserSchema = Depends(token_service.admin_required),
    ) -> FeatureGetViewSchema:

        return await self.feature_service.get(
            data=data,
        )
        

    @feature_router.post("/add", tags=["feature"])
    @try_rollback
    async def feature_add(
        self,
        data: FeatureAddSchema,
        _: UserSchema = Depends(token_service.director_required),
    ) -> FeatureAddViewSchema:
        return await self.feature_service.add(
            data=data,
        )