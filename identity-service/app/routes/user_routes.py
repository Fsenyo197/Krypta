from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.db import get_db
from app.utils.permission import permission_required
from app.utils.activity_logger import log_activity
from app.models.user_model import User
from app.utils.current_user import get_current_user

user_router = APIRouter(prefix="/users", tags=["Users"])


# -------------------------
# Create user
# -------------------------
@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@permission_required("user:create")
def create_user(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = UserService.create_user(db, user_in)
    log_activity(db, current_user, "user:create", request, user=user.username)
    return user


# -------------------------
# Get user by ID
# -------------------------
@user_router.get("/{user_id}", response_model=UserResponse)
@permission_required("user:read")
def get_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = UserService.get_user_by_id(db, user_id)
    log_activity(db, current_user, "user:read", request, user=user.username)
    return user


# -------------------------
# List users
# -------------------------
@user_router.get("/", response_model=List[UserResponse])
@permission_required("user:list")
def list_users(
    skip: int = 0,
    limit: int = 100,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = UserService.list_users(db, skip=skip, limit=limit)
    log_activity(db, current_user, "user:list", request)
    return users


# -------------------------
# Update user
# -------------------------
@user_router.put("/{user_id}", response_model=UserResponse)
@permission_required("user:update")
def update_user(
    user_id: str,
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = UserService.get_user_by_id(db, user_id)
    updated_user = UserService.update_user(db, user, user_in)
    log_activity(db, current_user, "user:update", request, user=updated_user.username)
    return updated_user


# -------------------------
# Delete user
# -------------------------
@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@permission_required("user:delete")
def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = UserService.get_user_by_id(db, user_id)
    UserService.delete_user(db, user)
    log_activity(db, current_user, "user:delete", request, user=user.username)
    return {"detail": "User deleted successfully"}
