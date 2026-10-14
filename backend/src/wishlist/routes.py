import uuid

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import User

from .schemas import WishlistItemAdd, WishlistOut
from .service import WishlistService

wishlist_router = APIRouter()
service = WishlistService()


@wishlist_router.get("", response_model=WishlistOut)
async def get_wishlist(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await service.get_wishlist(current_user.uid, session)


@wishlist_router.post("", response_model=WishlistOut)
async def add_to_wishlist(
    data: WishlistItemAdd,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.add(current_user.uid, data.product_id, session)


@wishlist_router.delete("/{product_id}", response_model=WishlistOut)
async def remove_from_wishlist(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.remove(current_user.uid, product_id, session)
