import math
import uuid
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func, select as sa_select
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Product, ProductImage, Vendor

from .schemas import ProductCreate, ProductListOut, ProductOut, ProductUpdate


class ProductService:
    async def _attach_images(self, product: Product, urls: List[str], session: AsyncSession) -> None:
        """Replace product images with new list."""
        # delete existing
        existing = await session.exec(select(ProductImage).where(ProductImage.product_id == product.uid))
        for img in existing.all():
            await session.delete(img)
        # add new
        for pos, url in enumerate(urls):
            session.add(ProductImage(product_id=product.uid, url=url, position=pos))

    async def get_all(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        category_slug: Optional[str] = None,
        vendor_slug: Optional[str] = None,
        query: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        in_stock: Optional[bool] = None,
        sort: str = "newest",
    ) -> ProductListOut:
        from src.db.models import Category

        stmt = select(Product).where(Product.status == "active")

        if category_slug:
            cat_q = await session.exec(select(Category).where(Category.slug == category_slug))
            cat = cat_q.first()
            if cat:
                stmt = stmt.where(Product.category_id == cat.uid)

        if vendor_slug:
            v_q = await session.exec(select(Vendor).where(Vendor.slug == vendor_slug))
            vendor = v_q.first()
            if vendor:
                stmt = stmt.where(Product.vendor_id == vendor.uid)

        if query:
            stmt = stmt.where(Product.title.ilike(f"%{query.strip()}%"))

        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)
        if in_stock is True:
            stmt = stmt.where(Product.stock > 0)

        # sorting
        if sort == "price_asc":
            stmt = stmt.order_by(Product.price.asc())
        elif sort == "price_desc":
            stmt = stmt.order_by(Product.price.desc())
        elif sort == "rating":
            stmt = stmt.order_by(Product.rating_avg.desc())
        else:  # newest
            stmt = stmt.order_by(Product.created_at.desc())

        total_result = await session.exec(select(func.count()).select_from(stmt.subquery()))
        total = total_result.one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await session.exec(stmt)
        items = result.all()

        return ProductListOut(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total else 0,
        )

    async def get_by_slug(self, slug: str, session: AsyncSession) -> Optional[Product]:
        result = await session.exec(select(Product).where(Product.slug == slug, Product.status == "active"))
        return result.first()

    async def get_by_id(self, uid: uuid.UUID, session: AsyncSession) -> Optional[Product]:
        result = await session.exec(select(Product).where(Product.uid == uid))
        return result.first()

    async def get_vendor_products(
        self,
        vendor_id: uuid.UUID,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> ProductListOut:
        stmt = select(Product).where(Product.vendor_id == vendor_id).order_by(Product.created_at.desc())
        total_result = await session.exec(select(func.count()).select_from(stmt.subquery()))
        total = total_result.one()
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await session.exec(stmt)
        return ProductListOut(
            items=result.all(),
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total else 0,
        )

    async def create(self, vendor_id: uuid.UUID, data: ProductCreate, session: AsyncSession) -> Product:
        payload = data.model_dump(exclude={"image_urls"})
        payload["vendor_id"] = vendor_id
        payload["status"] = "active"
        product = Product(**payload)
        session.add(product)
        await session.flush()  # get uid before images
        await self._attach_images(product, data.image_urls, session)
        await session.commit()
        await session.refresh(product)
        return product

    async def update(self, product: Product, data: ProductUpdate, session: AsyncSession) -> Product:
        payload = data.model_dump(exclude_none=True, exclude={"image_urls"})
        for k, v in payload.items():
            setattr(product, k, v)
        if data.stock is not None:
            product.stock = data.stock
        if data.image_urls is not None:
            await self._attach_images(product, data.image_urls, session)
        await session.commit()
        await session.refresh(product)
        return product

    async def delete(self, product: Product, session: AsyncSession) -> None:
        product.status = "archived"
        await session.commit()
