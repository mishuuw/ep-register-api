from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.common.token_service import token_service
from src.config.settings import get_settings
from src.department.department_schema import (
    DepartmentGetViewSchema,
    DepartmentSchema,
    DepartmentUpdateSchema,
)
from src.department.department_service import DepartmentService
from src.user.user_schema import UserSchema
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

    @department_router.get("/get", tags=["department"])
    @try_rollback
    async def department_get(
        self,
    ) -> DepartmentGetViewSchema:
        return await self.department_service.department_get()

    @department_router.post("/add", tags=["department"])
    @try_rollback
    async def department_add(
        self,
        data: DepartmentSchema,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> AddViewSchema:
        return await self.department_service.department_add(data=data)

    @department_router.patch("/update", tags=["department"])
    @try_rollback
    async def department_update(
        self,
        data: DepartmentUpdateSchema,
        _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        return await self.department_service.department_update(data=data)

    @department_router.delete("/delete", tags=["department"])
    @try_rollback
    async def department_delete(
        self,
        department_id: int = Query(..., description="Department ID"),
        _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        return await self.department_service.department_delete(
            department_id=department_id
        )