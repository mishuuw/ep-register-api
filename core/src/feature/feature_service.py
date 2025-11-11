from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_repo import CommonRepository
from src.feature.feature_schema import FeatureAddSchema, FeatureAddViewSchema, FeatureGetSchema, FeatureGetViewSchema
from src.feature.feature_usecase import FeatureUsecase
from src.feature.feature_repo import FeatureRepository
from src.utils.common_util import timeit


class FeatureService:
    def __init__(
        self,
        session: AsyncSession,
        back: BackgroundTasks,
        lang: Literal["ru", "en"],
    ):
        self.lang = lang
        self.back = back
        self.session = session

        self.feature_usecase = FeatureUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.common_repo = CommonRepository(session=session)
        self.feature_repo = FeatureRepository(
            lang=lang,
            back=back,
            session=session,
        )

    async def get(
        self,
        data: FeatureGetSchema,
    ) -> FeatureGetViewSchema:
        pass

    @timeit
    async def add(
        self,
        data: FeatureAddSchema,
    ) -> FeatureAddViewSchema:
        return FeatureAddViewSchema(
            id=-1,
        )