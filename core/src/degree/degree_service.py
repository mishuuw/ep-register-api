from typing import Literal

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.common_exc import NotFoundHttpException
from src.common.common_repo import CommonRepository
from src.common.common_schema import AddViewSchema, SuccessSchema
from src.degree.degree_schema import (
    DegreeAddSchema,
    DegreeGetSchema,
    DegreeGetViewSchema,
    DegreeUpdateSchema,
)
from src.degree.degree_usecase import DegreeUsecase
from src.degree.degree_repo import DegreeRepository
from src.models.degree import DegreeOrm
from src.utils.common_util import timeit


class DegreeService:
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
        self.degree_usecase = DegreeUsecase(
            session=session,
            back=back,
            lang=lang,
        )
        self.degree_repo = DegreeRepository(
            lang=lang,
            back=back,
            session=session,
        )
        
    async def degree_delete(
        self,
        degree_id: int,
    ) -> SuccessSchema:
        degree = await self.common_repo.get_one(
            DegreeOrm,
            DegreeOrm.id == degree_id
        )
        if not degree:
            raise NotFoundHttpException("degree")
        
        await self.common_repo.delete(
            DegreeOrm,
            DegreeOrm.id == degree.id
        )
        return SuccessSchema(detail="success")
    
    async def degree_update(
        self,
        data: DegreeUpdateSchema,
    ) -> SuccessSchema:
        degree = await self.common_repo.get_one(
            DegreeOrm,
            DegreeOrm.id == data.id
        )
        if not degree:
            raise NotFoundHttpException("degree")
    
        data_dict = data.model_dump(exclude_none=True)
        result = await self.common_repo.update(
            DegreeOrm(
                **data_dict
            )
        )
        if result.id:
            return SuccessSchema(detail="success")
        
    async def degree_add(
        self,
        data: DegreeAddSchema,
    ) -> AddViewSchema:
        degree = await self.common_repo.add(
            DegreeOrm(
                title=data.title,
            )
        )
        return AddViewSchema(
            id = degree.id
        )
            
        
    async def degree_get(self) -> DegreeGetViewSchema:
        result = await self.common_repo.get_all_scalars(
            DegreeOrm
        )
        
        return DegreeGetViewSchema(
            count=len(result),
            result=[
                DegreeGetSchema(
                    id=degree.id, 
                    title=degree.title
                ) for degree in result
            ],   
        )