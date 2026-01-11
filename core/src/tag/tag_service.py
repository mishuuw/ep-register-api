from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.tag.tag_repo import TagRepository
from src.tag.tag_schema import (
    TagUpdateSchema,
    TagSchema,
    TagGetViewSchema,
    TagGetSchema
)
from src.tag.tag_usecase import TagUsecase
from src.models.tag import TagOrm
from src.models.enum import TagTypeEnum


class TagService:
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
        self.tag_usecase = TagUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.tag_repo = TagRepository(
            lang=lang,
            back=back,
            session=session,
        )

    async def tag_delete(
        self,
        tag_id: int,
    ) -> SuccessSchema:
        tag = await self.common_repo.get_one(
            TagOrm,
            TagOrm.id == tag_id,
        )
        if not tag:
            raise NotFoundHttpException(name="Tag")

        await self.common_repo.delete(
            TagOrm,
            TagOrm.id == tag.id,
        )

        return SuccessSchema(detail="success")

    async def tag_update(
        self,
        data: TagUpdateSchema,
    ) -> SuccessSchema:
        tag = await self.common_repo.get_one(
            TagOrm,
            TagOrm.id == data.id,
        )
        if not tag:
            raise NotFoundHttpException(name="Tag")

        data_dict = data.model_dump(exclude_unset=True)
        
        if not data_dict:
            return SuccessSchema(detail="success")
        
        await self.common_repo.update(
            TagOrm(
                **data_dict,
            )
        )

        return SuccessSchema(detail="success")
    
    async def tag_add(
        self,
        data: TagSchema,
    ) -> AddViewSchema:
        tag_type = TagTypeEnum(data.type)
        
        tag = await self.common_repo.add(
            TagOrm(
                name=data.name,
                type=tag_type,
                boolean_value=data.boolean_value if tag_type == TagTypeEnum.BOOLEAN else None,
                number_value=data.number_value if tag_type == TagTypeEnum.NUMBER else None,
                text_value=data.text_value if tag_type == TagTypeEnum.TEXT else None,
            )
        )
        return AddViewSchema(id=tag.id)
    
    async def tag_get(
        self,
    ) -> TagGetViewSchema:
        tags = await self.common_repo.get_all_scalars(
            TagOrm,
        )

        return TagGetViewSchema(
            count=len(tags),
            result=[
                TagGetSchema(
                    id=tag.id,
                    name=tag.name,
                    type=tag.type,
                    value=tag.get_value(),
                ) for tag in tags
            ],
        )
    