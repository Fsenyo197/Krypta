from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.user_model import User, UserStatus
from app.db import get_db
import os

# OAuth2 scheme for extracting Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Environment-based JWT config
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and return the current authenticated user based on JWT token.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate JWT
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")   # Standard claim
        if not user_id:
            raise credentials_exception

        # Ensure valid UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise credentials_exception

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    # Fetch user from DB
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check account status
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status.value}",
        )

    return user
