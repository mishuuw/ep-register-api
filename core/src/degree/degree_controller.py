from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.common.token_service import token_service
from src.config.settings import get_settings
from src.degree.degree_schema import (
    DegreeAddSchema,
    DegreeGetViewSchema,
    DegreeUpdateSchema,
)
from src.degree.degree_service import DegreeService
from src.user.user_schema import UserSchema
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

degree_router = APIRouter()
settings = get_settings()


@cbv(degree_router)
class DegreeController:
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

        self.degree_service = DegreeService(
            lang=lang,
            back=back,
            session=session,
        )

    @degree_router.get("/get", tags=["degree"])
    @try_rollback
    async def degree_get(self) -> DegreeGetViewSchema:
        return await self.degree_service.degree_get()

    @degree_router.post("/add", tags=["degree"])
    @try_rollback
    async def degree_add(
        self,
        data: DegreeAddSchema,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> AddViewSchema:
        return await self.degree_service.degree_add(data=data)

    @degree_router.patch("/update", tags=["degree"])
    @try_rollback
    async def degree_update(
        self,
        data: DegreeUpdateSchema,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        return await self.degree_service.degree_update(data=data)

    @degree_router.delete("/delete", tags=["degree"])
    @try_rollback
    async def degree_delete(
        self,
        degree_id: int = Query(..., description="Degree ID"),
        _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        return await self.degree_service.degree_delete(degree_id=degree_id)
