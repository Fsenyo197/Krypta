from fastapi import APIRouter, Depends, Request, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import timedelta
from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.db import get_db
from app.utils.jwt import create_access_token, create_refresh_token
from app.schemas.user_schema import UserResponse
from app.utils.activity_logger import log_activity

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


# -------------------------
# Login
# -------------------------
@auth_router.post("/login", response_model=UserResponse)
def login(
    request: Request,
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    """Authenticate user, create session, and return JWTs."""
    user = UserService.authenticate_user(db, email, password)
    if not user:
        # Log failed login attempt
        log_activity(db, None, "login_failed", request=request, current_user=None, actor=email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate tokens
    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    # Create session via service
    SessionService.create_session(
        db=db,
        user_id=user.id,
        refresh_token=refresh_token,
        expires_delta=refresh_token_expires,
        user_agent=request.headers.get("user-agent", "unknown"),
        ip_address=request.client.host if request.client else None,
    )

    # Log successful login (actor = target = user)
    log_activity(db, user, "login", request=request, current_user=user)

    return {
        "user": UserResponse.from_orm(user),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# -------------------------
# Logout
# -------------------------
@auth_router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(UserService.authenticate_user), 
):
    """Invalidate session and log activity."""
    refresh_token = request.headers.get("X-Refresh-Token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token missing from headers"
        )

    SessionService.invalidate_session(db, refresh_token, user.id)

    # Log logout (actor = target = user)
    log_activity(db, user, "logout", request=request, current_user=user)

    return {"message": "Logged out successfully"}