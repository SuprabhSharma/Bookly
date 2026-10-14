import logging
import uuid
from decimal import Decimal

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Product, Review
from src.errors import BookNotFound, ProductNotFound, UserNotFound

from .schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self, user_email: str, book_uid: str, review_data: ReviewCreateModel, session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            user = await user_service.get_user_by_email(email=user_email, session=session)
            if not book:
                raise BookNotFound()
            if not user:
                raise UserNotFound()
            new_review = Review(**review_data.model_dump(), user=user, book=book)
            session.add(new_review)
            await session.commit()
            return new_review
        except Exception as e:
            logging.exception(e)
            raise HTTPException(detail="Oops... something went wrong!", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def add_review_to_product(
        self, user_email: str, product_id: uuid.UUID, review_data: ReviewCreateModel, session: AsyncSession,
    ):
        user = await user_service.get_user_by_email(email=user_email, session=session)
        if not user:
            raise UserNotFound()
        p_result = await session.exec(select(Product).where(Product.uid == product_id))
        product = p_result.first()
        if not product:
            raise ProductNotFound()
        review = Review(**review_data.model_dump(), user_id=user.uid, product_id=product.uid)
        session.add(review)
        await session.flush()
        # update denorm fields
        avg_result = await session.exec(
            select(func.avg(Review.rating), func.count(Review.uid))
            .where(Review.product_id == product.uid)
        )
        avg, cnt = avg_result.one()
        product.rating_avg = Decimal(str(avg or 0)).quantize(Decimal("0.01"))
        product.rating_count = cnt or 0
        await session.commit()
        await session.refresh(review)
        return review

    async def get_review(self, review_uid: str, session: AsyncSession):
        result = await session.exec(select(Review).where(Review.uid == review_uid))
        return result.first()

    async def get_all_reviews(self, session: AsyncSession):
        result = await session.exec(select(Review).order_by(desc(Review.created_at)))
        return result.all()

    async def delete_review_to_from_book(self, review_uid: str, user_email: str, session: AsyncSession):
        user = await user_service.get_user_by_email(user_email, session)
        review = await self.get_review(review_uid, session)
        if not review or (review.user_id != user.uid):
            raise HTTPException(detail="Cannot delete this review", status_code=status.HTTP_403_FORBIDDEN)
        await session.delete(review)
        await session.commit()