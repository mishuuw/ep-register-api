from collections import defaultdict
from typing import Literal, List

from fastapi import BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import get_settings
from src.models.educational_program import EducationalProgramOrm
from src.models.tag import TagOrm, TagToEducationalProgramOrm
from src.tag.tag_schema import (
    TagGroupedSchema,
    TagGroupedViewSchema,
    TagValueSchema,
)

settings = get_settings()


class TagRepository:
    def __init__(
        self,
        lang: Literal["ru", "en"],
        back: BackgroundTasks,
        session: AsyncSession,
    ):
        self.lang = lang
        self.back = back
        self.session = session

    async def get_tags_grouped_by_name(self) -> TagGroupedViewSchema:
        """Get all tags grouped by name (same name, different values)"""
        tags = (await self.session.execute(
            select(TagOrm).order_by(TagOrm.name, TagOrm.id)
        )).scalars().all()

        grouped: dict[str, List[TagValueSchema]] = defaultdict(list)
        for tag in tags:
            grouped[tag.name].append(
                TagValueSchema(
                    id=tag.id,
                    value=tag.get_value(),
                    type=tag.type.value,
                )
            )

        result = [
            TagGroupedSchema(name=name, values=values)
            for name, values in grouped.items()
        ]

        return TagGroupedViewSchema(
            count=len(result),
            result=result,
        )

    async def get_family_program_ids(self, educational_program_id: int) -> List[int]:
        """Get all program IDs in the family (including ancestors and descendants)"""
        # Find the root of the family (top-most ancestor)
        current = educational_program_id
        parent = await self.session.scalar(
            select(EducationalProgramOrm.parent_id).where(
                EducationalProgramOrm.id == current
            )
        )
        while parent is not None:
            current = parent
            parent = await self.session.scalar(
                select(EducationalProgramOrm.parent_id).where(
                    EducationalProgramOrm.id == current
                )
            )
        root_id = current

        # Get all descendants from root
        program_tree = (
            select(EducationalProgramOrm.id)
            .where(EducationalProgramOrm.id == root_id)
            .cte(name="program_tree", recursive=True)
        )

        program_tree = program_tree.union_all(
            select(EducationalProgramOrm.id).where(
                EducationalProgramOrm.parent_id == program_tree.c.id
            )
        )

        rows = (await self.session.execute(select(program_tree.c.id))).scalars().all()
        return list(rows)

    async def get_tags_for_programs(self, program_ids: List[int]) -> dict[int, dict]:
        """Get tags for multiple programs"""
        if not program_ids:
            return {}

        rows = (
            await self.session.execute(
                select(TagToEducationalProgramOrm, TagOrm)
                .where(
                    TagToEducationalProgramOrm.educational_program_id.in_(program_ids)
                )
                .join(
                    TagOrm,
                    TagOrm.id == TagToEducationalProgramOrm.tag_id,
                )
            )
        ).all()

        grouped: dict[int, dict[str, dict]] = defaultdict(dict)

        for junction, tag in rows:
            if tag is None:
                continue

            program_id = junction.educational_program_id
            tag_name = tag.name
            tag_type = tag.type.value
            value = tag.get_value()

            grouped[program_id][tag_name] = {
                "id": tag.id,
                "value": value,
                "type": tag_type
            }

        return dict(grouped)
