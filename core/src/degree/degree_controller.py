from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.auth.auth_service import AuthService
from src.config.settings import get_settings
from src.degree.degree_schema import (
    DegreeAddSchema,
    DegreeGetViewSchema,
    DegreeUpdateSchema,
)
from src.degree.degree_service import DegreeService
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
        self.auth_service = AuthService(
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
        request: Request,
        response: Response,
        data: DegreeAddSchema,
    ) -> AddViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.degree_service.degree_add(data=data)

    @degree_router.patch("/update", tags=["degree"])
    @try_rollback
    async def degree_update(
        self,
        request: Request,
        response: Response,
        data: DegreeUpdateSchema,
    ) -> None:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.degree_service.degree_update(data=data)

    @degree_router.delete("/delete", tags=["degree"])
    @try_rollback
    async def degree_delete(
        self,
        request: Request,
        response: Response,
        degree_id: int = Query(..., description="Degree ID"),
    ) -> None:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.degree_service.degree_delete(degree_id=degree_id)
