import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import User, Vendor
from src.errors import VendorNotFound

from .schemas import CheckoutRequest, OrderOut, SubOrderOut, SubOrderStatusUpdate
from .service import OrderService

order_router = APIRouter()
service = OrderService()


async def get_approved_vendor(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Vendor:
    from sqlmodel import select
    result = await session.exec(select(Vendor).where(Vendor.user_id == current_user.uid, Vendor.status == "approved"))
    vendor = result.first()
    if not vendor:
        raise VendorNotFound()
    return vendor


# ── Customer ──────────────────────────────────────────────────────────────────

@order_router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.checkout(current_user.uid, data, session)


@order_router.get("", response_model=List[OrderOut])
async def list_orders(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await service.get_user_orders(current_user.uid, session)


@order_router.get("/{uid}", response_model=OrderOut)
async def get_order(
    uid: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_order(uid, current_user.uid, session)


@order_router.post("/{uid}/cancel", response_model=OrderOut)
async def cancel_order(
    uid: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.cancel_order(uid, current_user.uid, session)


# ── Vendor ────────────────────────────────────────────────────────────────────

@order_router.patch("/vendor/sub-orders/{sub_uid}/status", response_model=SubOrderOut)
async def update_suborder_status(
    sub_uid: uuid.UUID,
    data: SubOrderStatusUpdate,
    vendor: Vendor = Depends(get_approved_vendor),
    session: AsyncSession = Depends(get_session),
):
    return await service.update_suborder_status(sub_uid, vendor.uid, data.status, session)
