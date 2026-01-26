from typing import Literal, List

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, SuccessSchema, DependencyCheckSchema
from src.tag.tag_repo import TagRepository
from src.tag.tag_schema import (
    TagUpdateSchema,
    TagSchema,
    TagGetViewSchema,
    TagGetSchema,
    TagGroupedViewSchema,
    TagToFamilyAddSchema,
    TagToFamilyRemoveSchema,
    TagToFamilyUpdateSchema,
    TagToProgramAddSchema,
    TagToProgramRemoveSchema,
    TagToProgramUpdateSchema,
)
from src.tag.tag_usecase import TagUsecase
from src.models.tag import TagOrm, TagToEducationalProgramOrm
from src.models.educational_program import EducationalProgramOrm
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

    async def tag_get_grouped(self) -> TagGroupedViewSchema:
        """Get all tags grouped by name"""
        return await self.tag_repo.get_tags_grouped_by_name()

    async def _validate_tags_exist(self, tag_ids: List[int]) -> None:
        """Validate that all tag IDs exist"""
        if not tag_ids:
            return
        
        dependencies = [
            DependencyCheckSchema(table=TagOrm, id=tag_id)
            for tag_id in tag_ids
        ]
        missing = await self.common_repo.check_dependencies(dependencies)
        if missing is not True:
            raise NotFoundHttpException(name="Tag")

    async def _validate_program_exists(self, program_id: int) -> None:
        """Validate that program exists"""
        program = await self.common_repo.get_one(
            EducationalProgramOrm,
            EducationalProgramOrm.id == program_id,
        )
        if not program:
            raise NotFoundHttpException(name="EducationalProgram")

    async def tag_to_program_add(
        self,
        data: TagToProgramAddSchema,
    ) -> SuccessSchema:
        """Add tags to a single educational program"""
        await self._validate_program_exists(data.educational_program_id)
        await self._validate_tags_exist(data.tag_ids)

        existing = await self.common_repo.get_all_scalars(
            TagToEducationalProgramOrm,
            TagToEducationalProgramOrm.educational_program_id == data.educational_program_id,
        )
        existing_tag_ids = {link.tag_id for link in existing}

        new_tags = [
            TagToEducationalProgramOrm(
                educational_program_id=data.educational_program_id,
                tag_id=tag_id,
            )
            for tag_id in data.tag_ids
            if tag_id not in existing_tag_ids
        ]

        if new_tags:
            await self.common_repo.add_all(new_tags)

        return SuccessSchema(detail="success")

    async def tag_to_program_remove(
        self,
        data: TagToProgramRemoveSchema,
    ) -> SuccessSchema:
        """Remove tags from a single educational program"""
        await self._validate_program_exists(data.educational_program_id)

        if data.tag_ids:
            await self.common_repo.delete(
                TagToEducationalProgramOrm,
                (
                    TagToEducationalProgramOrm.educational_program_id == data.educational_program_id,
                    TagToEducationalProgramOrm.tag_id.in_(data.tag_ids),
                ),
            )

        return SuccessSchema(detail="success")

    async def tag_to_program_update(
        self,
        data: TagToProgramUpdateSchema,
    ) -> SuccessSchema:
        """Replace all tags for a single educational program"""
        await self._validate_program_exists(data.educational_program_id)
        await self._validate_tags_exist(data.tag_ids)

        # Delete all existing tag links
        await self.common_repo.delete(
            TagToEducationalProgramOrm,
            TagToEducationalProgramOrm.educational_program_id == data.educational_program_id,
        )

        # Add new tag links
        if data.tag_ids:
            await self.common_repo.add_all([
                TagToEducationalProgramOrm(
                    educational_program_id=data.educational_program_id,
                    tag_id=tag_id,
                )
                for tag_id in data.tag_ids
            ])

        return SuccessSchema(detail="success")

    async def tag_to_family_add(
        self,
        data: TagToFamilyAddSchema,
    ) -> SuccessSchema:
        """Add tags to all programs in a family (entire hierarchy)"""
        await self._validate_program_exists(data.educational_program_id)
        await self._validate_tags_exist(data.tag_ids)

        family_ids = await self.tag_repo.get_family_program_ids(data.educational_program_id)

        existing = await self.common_repo.get_all_scalars(
            TagToEducationalProgramOrm,
            TagToEducationalProgramOrm.educational_program_id.in_(family_ids),
        )
        existing_pairs = {(link.educational_program_id, link.tag_id) for link in existing}

        new_tags = []
        for program_id in family_ids:
            for tag_id in data.tag_ids:
                if (program_id, tag_id) not in existing_pairs:
                    new_tags.append(
                        TagToEducationalProgramOrm(
                            educational_program_id=program_id,
                            tag_id=tag_id,
                        )
                    )

        if new_tags:
            await self.common_repo.add_all(new_tags)

        return SuccessSchema(detail="success")

    async def tag_to_family_remove(
        self,
        data: TagToFamilyRemoveSchema,
    ) -> SuccessSchema:
        """Remove tags from all programs in a family (entire hierarchy)"""
        await self._validate_program_exists(data.educational_program_id)

        if not data.tag_ids:
            return SuccessSchema(detail="success")

        family_ids = await self.tag_repo.get_family_program_ids(data.educational_program_id)

        await self.common_repo.delete(
            TagToEducationalProgramOrm,
            (
                TagToEducationalProgramOrm.educational_program_id.in_(family_ids),
                TagToEducationalProgramOrm.tag_id.in_(data.tag_ids),
            ),
        )

        return SuccessSchema(detail="success")

    async def tag_to_family_update(
        self,
        data: TagToFamilyUpdateSchema,
    ) -> SuccessSchema:
        """Replace all tags for all programs in a family (entire hierarchy)"""
        await self._validate_program_exists(data.educational_program_id)
        await self._validate_tags_exist(data.tag_ids)

        family_ids = await self.tag_repo.get_family_program_ids(data.educational_program_id)

        await self.common_repo.delete(
            TagToEducationalProgramOrm,
            TagToEducationalProgramOrm.educational_program_id.in_(family_ids),
        )

        if data.tag_ids:
            new_tags = []
            for program_id in family_ids:
                for tag_id in data.tag_ids:
                    new_tags.append(
                        TagToEducationalProgramOrm(
                            educational_program_id=program_id,
                            tag_id=tag_id,
                        )
                    )
            await self.common_repo.add_all(new_tags)

        return SuccessSchema(detail="success")
    