from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db import get_db
from app.schemas.staff_schema import StaffCreate, StaffUpdate, StaffResponse
from app.services import staff_service

staff_router = APIRouter(prefix="/staff", tags=["Staff"])


@staff_router.post("/", response_model=StaffResponse)
def create_staff(staff_data: StaffCreate, db: Session = Depends(get_db)):
    return staff_service.create_staff(db, staff_data)


@staff_router.get("/{staff_id}", response_model=StaffResponse)
def get_staff(staff_id: UUID, db: Session = Depends(get_db)):
    return staff_service.get_staff(db, staff_id)


@staff_router.get("/", response_model=List[StaffResponse])
def list_staff(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return staff_service.list_staff(db, skip, limit)


@staff_router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(staff_id: UUID, staff_data: StaffUpdate, db: Session = Depends(get_db)):
    return staff_service.update_staff(db, staff_id, staff_data)


@staff_router.delete("/{staff_id}")
def delete_staff(staff_id: UUID, db: Session = Depends(get_db)):
    return staff_service.delete_staff(db, staff_id)
