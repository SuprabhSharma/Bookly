import uuid
from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Address

from .schemas import AddressCreate, AddressUpdate


class AddressService:
    async def get_all(self, user_id: uuid.UUID, session: AsyncSession) -> List[Address]:
        result = await session.exec(select(Address).where(Address.user_id == user_id))
        return result.all()

    async def get_by_id(self, uid: uuid.UUID, user_id: uuid.UUID, session: AsyncSession) -> Optional[Address]:
        result = await session.exec(
            select(Address).where(Address.uid == uid, Address.user_id == user_id)
        )
        return result.first()

    async def create(self, user_id: uuid.UUID, data: AddressCreate, session: AsyncSession) -> Address:
        if data.is_default:
            # unset other defaults
            existing = await session.exec(select(Address).where(Address.user_id == user_id, Address.is_default == True))
            for a in existing.all():
                a.is_default = False
        addr = Address(**data.model_dump(), user_id=user_id)
        session.add(addr)
        await session.commit()
        await session.refresh(addr)
        return addr

    async def update(self, addr: Address, data: AddressUpdate, session: AsyncSession) -> Address:
        if data.is_default:
            existing = await session.exec(
                select(Address).where(Address.user_id == addr.user_id, Address.is_default == True)
            )
            for a in existing.all():
                if a.uid != addr.uid:
                    a.is_default = False
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(addr, k, v)
        await session.commit()
        await session.refresh(addr)
        return addr

    async def delete(self, addr: Address, session: AsyncSession) -> None:
        await session.delete(addr)
        await session.commit()
