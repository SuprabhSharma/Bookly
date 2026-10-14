import uuid
from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Product, Wishlist
from src.errors import ProductNotFound

from .schemas import WishlistItemOut, WishlistOut


class WishlistService:
    async def get_wishlist(self, user_id: uuid.UUID, session: AsyncSession) -> WishlistOut:
        result = await session.exec(select(Wishlist).where(Wishlist.user_id == user_id))
        items = result.all()
        out = []
        for w in items:
            if w.product:
                out.append(WishlistItemOut(
                    uid=w.uid,
                    product_id=w.product_id,
                    product_title=w.product.title,
                    product_slug=w.product.slug,
                    created_at=w.created_at,
                ))
        return WishlistOut(items=out, total=len(out))

    async def add(self, user_id: uuid.UUID, product_id: uuid.UUID, session: AsyncSession) -> WishlistOut:
        p_result = await session.exec(select(Product).where(Product.uid == product_id))
        if not p_result.first():
            raise ProductNotFound()
        # idempotent
        existing = await session.exec(
            select(Wishlist).where(Wishlist.user_id == user_id, Wishlist.product_id == product_id)
        )
        if not existing.first():
            session.add(Wishlist(user_id=user_id, product_id=product_id))
            await session.commit()
        return await self.get_wishlist(user_id, session)

    async def remove(self, user_id: uuid.UUID, product_id: uuid.UUID, session: AsyncSession) -> WishlistOut:
        result = await session.exec(
            select(Wishlist).where(Wishlist.user_id == user_id, Wishlist.product_id == product_id)
        )
        item = result.first()
        if item:
            await session.delete(item)
            await session.commit()
        return await self.get_wishlist(user_id, session)
