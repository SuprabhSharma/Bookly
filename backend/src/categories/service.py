import uuid
from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Category
from .schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    async def get_all(self, session: AsyncSession) -> list[Category]:
        result = await session.exec(select(Category))
        return result.all()

    async def get_by_slug(self, slug: str, session: AsyncSession) -> Optional[Category]:
        result = await session.exec(select(Category).where(Category.slug == slug))
        return result.first()

    async def get_by_id(self, uid: uuid.UUID, session: AsyncSession) -> Optional[Category]:
        result = await session.exec(select(Category).where(Category.uid == uid))
        return result.first()

    async def create(self, data: CategoryCreate, session: AsyncSession) -> Category:
        cat = Category(**data.model_dump())
        session.add(cat)
        await session.commit()
        await session.refresh(cat)
        return cat

    async def update(self, cat: Category, data: CategoryUpdate, session: AsyncSession) -> Category:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(cat, k, v)
        await session.commit()
        await session.refresh(cat)
        return cat

    async def delete(self, cat: Category, session: AsyncSession) -> None:
        await session.delete(cat)
        await session.commit()
