import uuid
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User, Vendor

from .schemas import VendorApply, VendorUpdate


class VendorService:
    async def get_by_slug(self, slug: str, session: AsyncSession) -> Optional[Vendor]:
        result = await session.exec(select(Vendor).where(Vendor.slug == slug, Vendor.status == "approved"))
        return result.first()

    async def get_by_id(self, uid: uuid.UUID, session: AsyncSession) -> Optional[Vendor]:
        result = await session.exec(select(Vendor).where(Vendor.uid == uid))
        return result.first()

    async def get_by_user_id(self, user_id: uuid.UUID, session: AsyncSession) -> Optional[Vendor]:
        result = await session.exec(select(Vendor).where(Vendor.user_id == user_id))
        return result.first()

    async def get_all_pending(self, session: AsyncSession):
        result = await session.exec(select(Vendor).where(Vendor.status == "pending"))
        return result.all()

    async def apply(self, user_id: uuid.UUID, data: VendorApply, session: AsyncSession) -> Vendor:
        vendor = Vendor(**data.model_dump(), user_id=user_id, status="pending")
        session.add(vendor)
        await session.commit()
        await session.refresh(vendor)
        return vendor

    async def update(self, vendor: Vendor, data: VendorUpdate, session: AsyncSession) -> Vendor:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(vendor, k, v)
        await session.commit()
        await session.refresh(vendor)
        return vendor

    async def set_status(self, vendor: Vendor, status: str, session: AsyncSession) -> Vendor:
        vendor.status = status
        user_result = await session.exec(select(User).where(User.uid == vendor.user_id))
        user = user_result.first()
        if user:
            user.role = "vendor" if status == "approved" else "customer"
        await session.commit()
        await session.refresh(vendor)
        return vendor
