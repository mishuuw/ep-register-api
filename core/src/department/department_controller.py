from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema
from src.department.department_schema import (
    DepartmentFilterSchema,
    DepartmentGetViewSchema,
    DepartmentAddSchema
)
from src.department.department_service import DepartmentService
from src.common.token_service import token_service
from src.config.settings import get_settings
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
        filter: DepartmentFilterSchema = Depends(),
    #    _: UserSchema = Depends(token_service.admin_required),
    ) -> DepartmentGetViewSchema:
        pass


    @department_router.post("/add", tags=["department"])
    @try_rollback
    async def department_add(
        self,
        data: DepartmentAddSchema,
    #    _: UserSchema = Depends(token_service.admin_required),
    ) -> AddViewSchema:
        pass
    
    @department_router.patch("/update", tags=["department"])
    @try_rollback
    async def department_update(
        self,
    #    _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        pass


    @department_router.delete("/delete", tags=["department"])
    @try_rollback
    async def department_delete(
        self,
    #    _: UserSchema = Depends(token_service.admin_required),
    ) -> None:
        pass
