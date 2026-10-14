from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from src.db.models import User
from src.errors import BookNotFound, InsufficientPermission

from .schemas import Book, BookCreateModel, BookUpdateModel, BookDetailModel
from src.books.service import BookService
from src.db.main import get_session


book_router = APIRouter()
book_service = BookService()
session_dependency = Depends(get_session)
access_token_bearer = AccessTokenBearer()
access_token_dependency = Depends(access_token_bearer)
role_checker = Depends(RoleChecker(["admin", "customer", "vendor"]))


@book_router.get("/", response_model=list[Book], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = session_dependency,
    _: dict = access_token_dependency,
):
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_uid}", response_model=list[Book], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = session_dependency,
    _: dict = access_token_dependency,
):
    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = session_dependency,
    token_details: dict = access_token_dependency,
) -> dict:
    user_id = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(book_data, user_id, session)
    return new_book


@book_router.get(
    "/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker]
)
async def get_book(
    book_uid: str,
    session: AsyncSession = session_dependency,
    _: dict = access_token_dependency,
) -> dict:
    book = await book_service.get_book(book_uid, session)

    if book is None:
        raise BookNotFound()  # Fix: was silently returning None

    return book


@book_router.patch("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = session_dependency,
    current_user: User = Depends(get_current_user),
) -> dict:
    book = await book_service.get_book(book_uid, session)

    if book is None:
        raise BookNotFound()

    # Ownership check: only the owning vendor or admin may edit
    if current_user.role != "admin" and str(book.user_id) != str(current_user.uid):
        raise InsufficientPermission()

    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    return updated_book


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = session_dependency,
    current_user: User = Depends(get_current_user),
):
    book = await book_service.get_book(book_uid, session)

    if book is None:
        raise BookNotFound()

    # Ownership check: only the owning vendor or admin may delete
    if current_user.role != "admin" and str(book.user_id) != str(current_user.uid):
        raise InsufficientPermission()

    await book_service.delete_book(book_uid, session)

    return {}