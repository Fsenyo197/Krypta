from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db import get_db
from app.schemas.staff_schema import StaffCreate, StaffUpdate, StaffResponse
from app.services import staff_service
from app.utils.permission import permission_required
from app.models.user_model import User
from app.utils.current_user import get_current_user

staff_router = APIRouter(prefix="/staff", tags=["Staff"])


# -------------------------
# Create staff
# -------------------------
@staff_router.post("/", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
@permission_required("staff:create")
def create_staff(
    staff_data: StaffCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return staff_service.create_staff(db, staff_data, actor=current_user.staff)


# -------------------------
# Get staff by ID
# -------------------------
@staff_router.get("/{staff_id}", response_model=StaffResponse)
@permission_required("staff:read")
def get_staff(
    staff_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return staff_service.get_staff(db, staff_id, actor=current_user.staff)


# -------------------------
# List staff
# -------------------------
@staff_router.get("/", response_model=List[StaffResponse])
@permission_required("staff:list")
def list_staff(
    skip: int = 0,
    limit: int = 50,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return staff_service.list_staff(db, skip, limit)


# -------------------------
# Update staff
# -------------------------
@staff_router.put("/{staff_id}", response_model=StaffResponse)
@permission_required("staff:update")
def update_staff(
    staff_id: UUID,
    staff_data: StaffUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return staff_service.update_staff(db, staff_id, staff_data, actor=current_user.staff)


# -------------------------
# Delete staff
# -------------------------
@staff_router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
@permission_required("staff:delete")
def delete_staff(
    staff_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return staff_service.delete_staff(db, staff_id, actor=current_user.staff)
