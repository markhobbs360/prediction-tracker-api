from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    GoogleLoginRequest,
    PasswordLoginRequest,
    UserOut,
)
from app.services.auth_service import create_jwt, verify_google_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=AuthResponse)
async def google_login(body: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    payload = verify_google_token(body.token, settings.GOOGLE_CLIENT_ID)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    # Enforce hosted domain
    hd = payload.get("hd", "")
    if hd != "fundmetric.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only fundmetric.com accounts are allowed",
        )

    email = payload["email"]
    name = payload.get("name", email.split("@")[0])
    picture = payload.get("picture")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(email=email, name=name, picture_url=picture)
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        user.name = name
        user.picture_url = picture
        await db.flush()

    token = create_jwt(user.id, settings.JWT_SECRET, settings.JWT_EXPIRY_HOURS)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def password_login(body: PasswordLoginRequest, db: AsyncSession = Depends(get_db)):
    if not settings.SHARED_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password login is not configured",
        )

    if body.password != settings.SHARED_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None:
        name = body.email.split("@")[0]
        user = User(email=body.email, name=name)
        db.add(user)
        await db.flush()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is deactivated")

    token = create_jwt(user.id, settings.JWT_SECRET, settings.JWT_EXPIRY_HOURS)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
