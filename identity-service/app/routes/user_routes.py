from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.db import get_db
from app.utils.current_user import get_current_user

user_router = APIRouter(prefix="/users", tags=["Users"])


# -------------------------
# Create user
# -------------------------
@user_router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    return UserService.create_user(db, user_in, current_user=current_user, request=request)


# -------------------------
# Get user by ID
# -------------------------
@user_router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    return UserService.get_user_by_id(db, user_id, current_user=current_user, request=request)


# -------------------------
# List users
# -------------------------
@user_router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    return UserService.list_users(db, current_user=current_user, skip=skip, limit=limit, request=request)


# -------------------------
# Update user
# -------------------------
@user_router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    user = UserService.get_user_by_id(db, user_id, current_user=current_user, request=request)
    return UserService.update_user(db, user, user_in, current_user=current_user, request=request)


# -------------------------
# Delete user
# -------------------------
@user_router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    user = UserService.get_user_by_id(db, user_id, current_user=current_user, request=request)
    UserService.delete_user(db, user, current_user=current_user, request=request)
    return {"detail": "User deleted successfully"}
