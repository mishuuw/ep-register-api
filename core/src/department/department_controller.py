from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.auth.auth_service import AuthService
from src.config.settings import get_settings
from src.department.department_schema import (
    DepartmentAddSchema,
    DepartmentFilterSchema,
    DepartmentGetViewSchema,
)
from src.department.department_service import DepartmentService
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

department_router = APIRouter()
settings = get_settings()


@cbv(department_router)
class DepartmentController:
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

        self.department_service = DepartmentService(
            lang=lang,
            back=back,
            session=session,
        )
        self.auth_service = AuthService(
            lang=lang,
            back=back,
            session=session,
        )

    @department_router.get("/get", tags=["department"])
    @try_rollback
    async def department_get(
        self,
        request: Request,
        response: Response,
        filter: DepartmentFilterSchema = Depends(),
    ) -> DepartmentGetViewSchema:
        await self.auth_service.manager_required(request=request, response=response)
        return await self.department_service.department_get(filter=filter)

    @department_router.post("/add", tags=["department"])
    @try_rollback
    async def department_add(
        self,
        request: Request,
        response: Response,
        data: DepartmentAddSchema,
    ) -> AddViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        return await self.department_service.department_add(data=data)

    @department_router.patch("/update", tags=["department"])
    @try_rollback
    async def department_update(
        self,
        request: Request,
        response: Response,
    ) -> None:
        await self.auth_service.admin_required(request=request, response=response)
        raise NotImplementedError

    @department_router.delete("/delete", tags=["department"])
    @try_rollback
    async def department_delete(
        self,
        request: Request,
        response: Response,
    ) -> None:
        await self.auth_service.admin_required(request=request, response=response)
        raise NotImplementedError
