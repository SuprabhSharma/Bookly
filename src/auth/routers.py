from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config
from src.db.main import get_session
from src.errors import InvalidCredentials, InvalidToken, UserAlreadyExists, UserNotFound
from src.mail import create_message, mail

from .dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from .schemas import (
    EmailModel,
    UserBooksModel,
    UserCreateModel,
    UserLoginModel,
)
from .service import TokenBlocklistService, UserService
from .utils import (
    create_access_tokens,
    create_url_safe_token,
    decode_url_safe_token,
    normalize_email,
    verify_password,
)

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()
token_blocklist_service = TokenBlocklistService()
role_checker = RoleChecker(["admin", "user"])
session_dependency = Depends(get_session)
refresh_token_dependency = Depends(RefreshTokenBearer())
access_token_dependency = Depends(AccessTokenBearer())
current_user_dependency = Depends(get_current_user)
role_dependency = Depends(role_checker)



@auth_router.post('/send_email')
async def send_email(emails:EmailModel):
    emails = emails.addresses
    
    html = "<h1>Welcome to Booklyz</h1>"
    
    message = create_message(
        recipients=emails,
        subject="Welcome",
        body=html
    )
    
    await mail.send_message(message)
    
    return {
        "message":"Email sent Successfully"
    }
    


  
    
    


@auth_router.post(
    "/signup",status_code=status.HTTP_201_CREATED
)
async def create_user_Account(
    user_data: UserCreateModel,
    session: AsyncSession = session_dependency,
):
    """
    Create user account using email , username ,first_name , last_name
    params :
        user_data : UserCreateModel
    """
    

    email = normalize_email(user_data.email)
    user_data = user_data.model_copy(update={"email": email})

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)
    
    token = create_url_safe_token({"email":email})
    
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    
    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click <a href="{link}">here</a> to verify your email.</p>
    
    """
    
    message = create_message(
            recipients=[email],
            subject="Verify your email",
            body=html_message
        )
        
    await mail.send_message(message)
    

    return {
        "message" : "Account Created ! Check you email to verify your account",
        "user" : new_user
    }
    

@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = session_dependency):

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) 



@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel, session: AsyncSession = session_dependency
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
async def get_new_access_token(token_details: dict = refresh_token_dependency):

    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():  # noqa: DTZ006
        new_access_token = create_access_tokens(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(user=current_user_dependency, _: bool = role_dependency):

    return user


@auth_router.get("/logout")
async def revoke_token(
    token_details: dict = access_token_dependency,
    session: AsyncSession = session_dependency,
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
