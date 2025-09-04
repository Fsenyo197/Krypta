from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from app.models.staff_model import Staff
from app.schemas.staff_schema import StaffCreate, StaffUpdate

def create_staff(db: Session, staff_data: StaffCreate):
    new_staff = Staff(
        user_id=staff_data.user_id,
        department=staff_data.department,
        role=staff_data.role,
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff


def get_staff(db: Session, staff_id: UUID):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found"
        )
    return staff


def list_staff(db: Session, skip: int = 0, limit: int = 50):
    return db.query(Staff).offset(skip).limit(limit).all()


def update_staff(db: Session, staff_id: UUID, staff_data: StaffUpdate):
    staff = get_staff(db, staff_id)

    if staff_data.department is not None:
        staff.department = staff_data.department
    if staff_data.role is not None:
        staff.role = staff_data.role
    if staff_data.permissions is not None:
        staff.permissions = staff_data.permissions

    db.commit()
    db.refresh(staff)
    return staff


def delete_staff(db: Session, staff_id: UUID):
    staff = get_staff(db, staff_id)
    db.delete(staff)
    db.commit()
    return {"message": "Staff deleted successfully"}
