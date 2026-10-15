from datetime import timedelta, timezone, datetime

from fastapi import APIRouter, BackgroundTasks, Body, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config
from src.audit import record_audit
from src.db.main import get_session
from src.errors import (
    InvalidCredentials,
    InvalidToken,
    UserAlreadyExists,
    UserNotFound,
)
from src.mail import create_message, mail

from .dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from .schemas import (
    EmailModel,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    UserBooksModel,
    UserCreateModel,
    UserLoginModel,
)
from .service import TokenBlocklistService, UserService
from .utils import (
    create_access_tokens,
    create_url_safe_token,
    decode_url_safe_token,
    generate_passwd_hash,
    normalize_email,
    verify_password,
    decode_token,
)

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()
token_blocklist_service = TokenBlocklistService()
role_checker = RoleChecker(["admin", "customer", "vendor"])
session_dependency = Depends(get_session)
refresh_token_dependency = Depends(RefreshTokenBearer())
access_token_dependency = Depends(AccessTokenBearer())
current_user_dependency = Depends(get_current_user)
role_dependency = Depends(role_checker)


@auth_router.post("/send_email")
async def send_email(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to Tavilo</h1>"

    message = create_message(
        recipients=emails,
        subject="Welcome",
        body=html,
    )

    await mail.send_message(message)

    return {"message": "Email sent Successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = session_dependency,
):
    """Create user account using email, username, first_name, last_name."""

    email = normalize_email(user_data.email)
    user_data = user_data.model_copy(update={"email": email})

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email, "purpose": "email-verification"})

    # Link points to FRONTEND, not API
    link = f"{Config.FRONTEND_URL}/verify-email/{token}"

    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click <a href="{link}">here</a> to verify your email address.</p>
    """

    message = create_message(
        recipients=[email],
        subject="Verify your email",
        body=html_message,
    )

    bg_tasks.add_task(mail.send_message, message)

    return {
        "message": "Account created! Check your email to verify your account.",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = session_dependency):
    token_data = decode_url_safe_token(token, max_age=24 * 60 * 60)

    if not token_data:
        raise InvalidToken()

    if token_data.get("purpose") != "email-verification":
        raise InvalidToken()

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
        content={"message": "Error occurred during verification"},
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
            if user.role == "admin":
                await record_audit(
                    session,
                    "admin.login",
                    actor_user_id=user.uid,
                    metadata={"success": True},
                )
                await session.commit()
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
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid),
                        "role": user.role,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                }
            )

    raise InvalidCredentials()


@auth_router.post("/refresh_token")  # Changed from GET to POST
async def get_new_access_token(
    token_details: dict = refresh_token_dependency,
    session: AsyncSession = session_dependency,
):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp, tz=timezone.utc) > datetime.now(timezone.utc):
        # Re-read user from DB so the new access token always carries the current role
        user_email = token_details["user"]["email"]
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise InvalidToken()

        new_access_token = create_access_tokens(
            user_data={
                "email": user.email,
                "user_uid": str(user.uid),
                "role": user.role,
            }
        )

        await token_blocklist_service.revoke_token(
            token_details["jti"],
            datetime.fromtimestamp(token_details["exp"], tz=timezone.utc),
            session,
        )
        new_refresh_token = create_access_tokens(
            user_data={"email": user.email, "user_uid": str(user.uid)},
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
        )
        return JSONResponse(content={
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        })

    raise InvalidToken()


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user_me(user=current_user_dependency, _: bool = role_dependency):
    return user


@auth_router.post("/logout")  # Changed from GET to POST
async def revoke_token(
    token_details: dict = access_token_dependency,
    refresh_token: str | None = Body(default=None, embed=True),
    session: AsyncSession = session_dependency,
):
    jti = token_details["jti"]

    await token_blocklist_service.revoke_token(
        jti,
        datetime.fromtimestamp(token_details["exp"], tz=timezone.utc),  # Fixed: timezone.utc
        session,
    )
    if refresh_token:
        refresh_details = decode_token(refresh_token)
        if refresh_details and refresh_details.get("refresh"):
            await token_blocklist_service.revoke_token(
                refresh_details["jti"],
                datetime.fromtimestamp(refresh_details["exp"], tz=timezone.utc),
                session,
            )

    return JSONResponse(
        content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    # Always return the same response — do not reveal whether the email exists
    SUCCESS_RESPONSE = JSONResponse(
        content={
            "message": "If that email is registered, you will receive a password reset link shortly.",
        },
        status_code=status.HTTP_200_OK,
    )

    token = create_url_safe_token({"email": normalize_email(email), "purpose": "password-reset"})

    # Link points to FRONTEND, not API
    link = f"{Config.FRONTEND_URL}/reset-password/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click <a href="{link}">here</a> to reset your password.</p>
    """
    subject = "Reset Your Password"

    message = create_message(
        recipients=[email],
        subject=subject,
        body=html_message,
    )

    try:
        await mail.send_message(message)
    except Exception:
        pass  # Swallow silently — never reveal email existence

    return SUCCESS_RESPONSE


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = session_dependency,
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        return JSONResponse(
            content={"message": "Passwords do not match", "error_code": "password_mismatch"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token_data = decode_url_safe_token(token, max_age=60 * 60)

    if not token_data or token_data.get("purpose") != "password-reset":
        raise InvalidToken()

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        passwd_hash = generate_passwd_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occurred during password reset.", "error_code": "invalid_token"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
