from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from uuid import UUID
from app.models.staff_model import Staff, StaffRole, Department
from app.schemas.staff_schema import StaffCreate, StaffUpdate
from app.services.restriction_service import RestrictionService
from app.utils.activity_logger import log_activity


def create_staff(db: Session, staff_data: StaffCreate, actor: Staff = None, request: Request = None):
    try:
        # Ensure superuser uniqueness
        RestrictionService.ensure_single_superuser(db, staff_data.role, staff_data.department)

        new_staff = Staff(
            user_id=staff_data.user_id,
            department=staff_data.department,
            role=staff_data.role,
            permissions=staff_data.permissions,
        )
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)

        log_activity(
            db,
            target_user=new_staff.user,
            activity_type="create_staff_success",
            request=request,
            current_user=actor.user if actor else None,
            description=f"Staff {new_staff.id} created by {actor.user.username if actor else 'system'}"
        )

        return new_staff
    except HTTPException:
        raise
    except Exception as e:
        log_activity(
            db,
            target_user=actor.user if actor else None,
            activity_type="create_staff_error",
            request=request,
            current_user=actor.user if actor else None,
            description=str(e)
        )
        raise


def get_staff(db: Session, staff_id: UUID, actor: Staff = None, request: Request = None):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        log_activity(
            db,
            target_user=actor.user if actor else None,
            activity_type="get_staff_failed",
            request=request,
            current_user=actor.user if actor else None,
            description=f"Staff {staff_id} not found"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")

    if actor:
        RestrictionService.enforce(actor, staff, action="view")

    log_activity(
        db,
        target_user=staff.user,
        activity_type="get_staff_success",
        request=request,
        current_user=actor.user if actor else None,
        description=f"Staff {staff.id} retrieved by {actor.user.username if actor else 'system'}"
    )

    return staff


def list_staff(db: Session, skip: int = 0, limit: int = 50, actor: Staff = None, request: Request = None):
    staff_list = db.query(Staff).offset(skip).limit(limit).all()

    log_activity(
        db,
        target_user=actor.user if actor else None,
        activity_type="list_staff",
        request=request,
        current_user=actor.user if actor else None,
        description=f"Listed {len(staff_list)} staff records"
    )

    return staff_list


def update_staff(db: Session, staff_id: UUID, staff_data: StaffUpdate, actor: Staff, request: Request = None):
    try:
        staff = get_staff(db, staff_id, actor=actor, request=request)

        RestrictionService.enforce(actor, staff, action="edit")

        if staff_data.role == StaffRole.SUPERUSER or staff_data.department == Department.SUPERUSER:
            log_activity(
                db,
                target_user=actor.user,
                activity_type="update_staff_denied",
                request=request,
                current_user=actor.user,
                description="Attempt to update staff to SUPERUSER"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update staff to SUPERUSER")

        if staff_data.department is not None:
            staff.department = staff_data.department
        if staff_data.role is not None:
            staff.role = staff_data.role
        if staff_data.permissions is not None:
            staff.permissions = staff_data.permissions

        db.commit()
        db.refresh(staff)

        log_activity(
            db,
            target_user=staff.user,
            activity_type="update_staff_success",
            request=request,
            current_user=actor.user,
            description=f"Staff {staff.id} updated by {actor.user.username}"
        )

        return staff
    except HTTPException:
        raise
    except Exception as e:
        log_activity(
            db,
            target_user=actor.user,
            activity_type="update_staff_error",
            request=request,
            current_user=actor.user,
            description=str(e)
        )
        raise


def delete_staff(db: Session, staff_id: UUID, actor: Staff, request: Request = None):
    try:
        staff = get_staff(db, staff_id, actor=actor, request=request)

        RestrictionService.enforce(actor, staff, action="delete")

        db.delete(staff)
        db.commit()

        log_activity(
            db,
            target_user=staff.user,
            activity_type="delete_staff_success",
            request=request,
            current_user=actor.user,
            description=f"Staff {staff.id} deleted by {actor.user.username}"
        )

        return {"message": "Staff deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log_activity(
            db,
            target_user=actor.user,
            activity_type="delete_staff_error",
            request=request,
            current_user=actor.user,
            description=str(e)
        )
        raise
