from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.errors import InvalidCredentials, InvalidToken, UserAlreadyExists

from .dependencies import AccessTokenBearer, RefreshTokenBearer, get_current_user,RoleChecker
from .schemas import UserCreateModel, UserLoginModel, UserModel , UserBooksModel
from .service import TokenBlocklistService, UserService
from .utils import create_access_tokens, normalize_email, verify_password

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()
token_blocklist_service = TokenBlocklistService()
role_checker = RoleChecker(['admin','user'])


@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_Account(
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):

    email = normalize_email(user_data.email)
    user_data = user_data.model_copy(update={"email": email})

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    return new_user

@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_tokens(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = create_access_tokens(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

    raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):

    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():  # noqa: DTZ006
        new_access_token = create_access_tokens(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()
    
@auth_router.get('/me',response_model=UserBooksModel)
async def get_current_user(user = Depends(get_current_user) , _: bool = Depends(role_checker)):
    
    return user
    
    
    
    
    



@auth_router.get("/logout")
async def revoke_token(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):

    jti = token_details["jti"]

    await token_blocklist_service.revoke_token(
        jti,
        datetime.fromtimestamp(token_details["exp"], tz=timezone.utc),
        session,
    )

    return JSONResponse(
        content={"message": "Logged out Successfully"}, status_code=status.HTTP_200_OK
    )
    
    
