from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.auth.auth_service import AuthService
from src.config.settings import get_settings
from src.tag.tag_schema import (
    TagGetViewSchema,
    TagSchema,
    TagUpdateSchema,
    TagGroupedViewSchema,
    TagToFamilyAddSchema,
    TagToFamilyRemoveSchema,
    TagToFamilyUpdateSchema,
    TagToProgramAddSchema,
    TagToProgramRemoveSchema,
    TagToProgramUpdateSchema,
)
from src.tag.tag_service import (
    TagService,
)
from src.utils.common_util import try_rollback
from src.utils.db_util import get_session_obj

tag_router = APIRouter()
settings = get_settings()


@cbv(tag_router)
class TagController:
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

        self.tag_service = TagService(
            lang=lang,
            back=back,
            session=session,
        )
        self.auth_service = AuthService(
            lang=lang,
            back=back,
            session=session,
        )

    @tag_router.get("/get", tags=["tag"])
    @try_rollback
    async def tag_get(
        self,
        request: Request,
        response: Response,
    ) -> TagGetViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        service = self.tag_service
        return await service.tag_get()

    @tag_router.get("/grouped/get", tags=["tag"])
    @try_rollback
    async def tag_get_grouped(
        self,
        request: Request,
        response: Response,
    ) -> TagGroupedViewSchema:
        """Get all tags grouped by name (same name, different values)"""
        await self.auth_service.admin_required(request=request, response=response)
        service = self.tag_service
        return await service.tag_get_grouped()
    
    @tag_router.post("/add", tags=["tag"])
    @try_rollback
    async def tag_add(
        self,
        request: Request,
        response: Response,
        data: TagSchema,
    ) -> AddViewSchema:
        await self.auth_service.admin_required(request=request, response=response)
        service = self.tag_service
        return await service.tag_add(
            data=data,
        )
    
    @tag_router.patch("/update", tags=["tag"])
    @try_rollback
    async def tag_update(
        self,
        request: Request,
        response: Response,
        data: TagUpdateSchema,
    ) -> SuccessSchema:
        await self.auth_service.admin_required(request=request, response=response)
        service = self.tag_service
        return await service.tag_update(
            data=data,
        )
    
    @tag_router.delete("/delete", tags=["tag"])
    @try_rollback
    async def tag_delete(
        self,
        request: Request,
        response: Response,
        tag_id: int,
    ) -> SuccessSchema:
        await self.auth_service.admin_required(request=request, response=response)
        service = self.tag_service
        return await service.tag_delete(
            tag_id=tag_id,
        )

    @tag_router.post("/program/add", tags=["tag"])
    @try_rollback
    async def tag_to_program_add(
        self,
        request: Request,
        response: Response,
        data: TagToProgramAddSchema,
    ) -> SuccessSchema:
        """Add tags to a single educational program"""
        await self.auth_service.admin_required(request=request, response=response)
        return await self.tag_service.tag_to_program_add(data=data)

    @tag_router.post("/program/remove", tags=["tag"])
    @try_rollback
    async def tag_to_program_remove(
        self,
        request: Request,
        response: Response,
        data: TagToProgramRemoveSchema,
    ) -> SuccessSchema:
        """Remove tags from a single educational program"""
        await self.auth_service.admin_required(request=request, response=response)
        return await self.tag_service.tag_to_program_remove(data=data)

    @tag_router.put("/program/update", tags=["tag"])
    @try_rollback
    async def tag_to_program_update(
        self,
        request: Request,
        response: Response,
        data: TagToProgramUpdateSchema,
    ) -> SuccessSchema:
        """Replace all tags for a single educational program"""
        await self.auth_service.admin_required(request=request, response=response)
        return await self.tag_service.tag_to_program_update(data=data)

    @tag_router.post("/family/add", tags=["tag"])
    @try_rollback
    async def tag_to_family_add(
        self,
        request: Request,
        response: Response,
        data: TagToFamilyAddSchema,
    ) -> SuccessSchema:
        """Add tags to all programs in a family (entire hierarchy)"""
        await self.auth_service.admin_required(request=request, response=response)
        return await self.tag_service.tag_to_family_add(data=data)

    @tag_router.post("/family/remove", tags=["tag"])
    @try_rollback
    async def tag_to_family_remove(
        self,
        request: Request,
        response: Response,
        data: TagToFamilyRemoveSchema,
    ) -> SuccessSchema:
        """Remove tags from all programs in a family (entire hierarchy)"""
        await self.auth_service.admin_required(request=request, response=response)
        return await self.tag_service.tag_to_family_remove(data=data)

    @tag_router.put("/family/update", tags=["tag"])
    @try_rollback
    async def tag_to_family_update(
        self,
        request: Request,
        response: Response,
        data: TagToFamilyUpdateSchema,
    ) -> SuccessSchema:
        """Replace all tags for all programs in a family (entire hierarchy)"""
        await self.auth_service.admin_required(request=request, response=response)
        return await self.tag_service.tag_to_family_update(data=data)