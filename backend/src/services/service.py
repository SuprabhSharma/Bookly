import math
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import ServiceImage, ServiceOffering, Vendor

from .schemas import ServiceCreate, ServiceListOut, ServiceUpdate


class ServiceOfferingService:
    async def get_all(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        vendor_slug: Optional[str] = None,
    ) -> ServiceListOut:
        stmt = select(ServiceOffering).where(ServiceOffering.status == "active")
        if vendor_slug:
            vendor_result = await session.exec(select(Vendor).where(Vendor.slug == vendor_slug))
            vendor = vendor_result.first()
            if vendor:
                stmt = stmt.where(ServiceOffering.vendor_id == vendor.uid)
        stmt = stmt.order_by(ServiceOffering.created_at.desc())
        total = (await session.exec(select(func.count()).select_from(stmt.subquery()))).one()
        result = await session.exec(stmt.offset((page - 1) * page_size).limit(page_size))
        return ServiceListOut(
            items=result.all(),
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total else 0,
        )

    async def get_vendor_services(self, vendor_id: uuid.UUID, session: AsyncSession, page: int = 1, page_size: int = 100):
        stmt = select(ServiceOffering).where(ServiceOffering.vendor_id == vendor_id).order_by(ServiceOffering.created_at.desc())
        total = (await session.exec(select(func.count()).select_from(stmt.subquery()))).one()
        result = await session.exec(stmt.offset((page - 1) * page_size).limit(page_size))
        return ServiceListOut(items=result.all(), total=total, page=page, page_size=page_size, pages=math.ceil(total / page_size) if total else 0)

    async def get_by_id(self, uid: uuid.UUID, session: AsyncSession):
        return (await session.exec(select(ServiceOffering).where(ServiceOffering.uid == uid))).first()

    async def create(self, vendor_id: uuid.UUID, data: ServiceCreate, session: AsyncSession):
        payload = data.model_dump(exclude={"image_urls"})
        service = ServiceOffering(**payload, vendor_id=vendor_id, status="active")
        session.add(service)
        await session.flush()
        await self._attach_images(service, data.image_urls, session)
        await session.commit()
        await session.refresh(service)
        return service

    async def update(self, service: ServiceOffering, data: ServiceUpdate, session: AsyncSession):
        payload = data.model_dump(exclude_none=True, exclude={"image_urls"})
        for key, value in payload.items():
            setattr(service, key, value)
        if data.image_urls is not None:
            await self._attach_images(service, data.image_urls, session)
        await session.commit()
        await session.refresh(service)
        return service

    async def delete(self, service: ServiceOffering, session: AsyncSession):
        service.status = "archived"
        await session.commit()

    async def _attach_images(self, service: ServiceOffering, urls: list[str], session: AsyncSession):
        existing = await session.exec(select(ServiceImage).where(ServiceImage.service_id == service.uid))
        for image in existing.all():
            await session.delete(image)
        for position, url in enumerate(urls):
            session.add(ServiceImage(service_id=service.uid, url=url, position=position))
