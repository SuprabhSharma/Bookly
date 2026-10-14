import uuid

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import Product, Review, User
from src.errors import ProductNotFound, ReviewNotFound

from .schemas import ReviewCreateModel, ReviewModel, ReviewOut
from .service import ReviewService

product_review_router = APIRouter()
service = ReviewService()


# ── Product-scoped reviews ────────────────────────────────────────────────────

@product_review_router.get("/products/{slug}/reviews", response_model=list[ReviewOut])
async def get_product_reviews(slug: str, session: AsyncSession = Depends(get_session)):
    p_result = await session.exec(select(Product).where(Product.slug == slug))
    product = p_result.first()
    if not product:
        raise ProductNotFound()
    result = await session.exec(
        select(Review).where(Review.product_id == product.uid).order_by(Review.created_at.desc())
    )
    return result.all()


@product_review_router.post("/products/{product_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def add_product_review(
    product_id: uuid.UUID,
    data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.add_review_to_product(current_user.email, product_id, data, session)


# ── Legacy book reviews (backward compat) ─────────────────────────────────────

review_router = APIRouter()


@review_router.get("", response_model=list[ReviewOut])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    return await service.get_all_reviews(session)


@review_router.get("/{uid}", response_model=ReviewOut)
async def get_review(uid: uuid.UUID, session: AsyncSession = Depends(get_session)):
    review = await service.get_review(str(uid), session)
    if not review:
        raise ReviewNotFound()
    return review


@review_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    uid: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await service.delete_review_to_from_book(str(uid), current_user.email, session)
