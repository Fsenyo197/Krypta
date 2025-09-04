from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.db import get_db

user_router = APIRouter(prefix="/users", tags=["Users"])


# -------------------------
# Create user
# -------------------------
@user_router.post("/", response_model=UserResponse, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user_in)


# -------------------------
# Get user by ID
# -------------------------
@user_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    return UserService.get_user_by_id(db, user_id)


# -------------------------
# List users
# -------------------------
@user_router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return UserService.list_users(db, skip=skip, limit=limit)


# -------------------------
# Update user
# -------------------------
@user_router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id)
    return UserService.update_user(db, user, user_in)


# -------------------------
# Delete user
# -------------------------
@user_router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id)
    UserService.delete_user(db, user)
    return {"detail": "User deleted successfully"}

