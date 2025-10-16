from fastapi import HTTPException, status
from app.models.staff_model import Staff, StaffRole, Department
from app.models.user_model import User
from sqlalchemy.orm import Session


class RestrictionService:
    # ---------------- CORE RESTRICTION ---------------- #
    @staticmethod
    def enforce(actor: Staff, target: Staff, action: str):
        """
        Core restriction enforcement.
        Decides what staff can do to another staff based on their roles.
        Supported actions: 'view', 'edit', 'delete', 'create'
        """

        # Superuser restrictions
        if target.role == StaffRole.SUPERUSER:
            RestrictionService._enforce_superuser_rules(actor, target, action)

        # Admin restrictions
        elif target.role == StaffRole.ADMIN:
            RestrictionService._enforce_admin_rules(actor, target, action)

        # Future roles (support, compliance, etc.) can be added here
        # e.g., elif target.role == StaffRole.MANAGER: RestrictionService._enforce_manager_rules(...)

    # ---------------- SUPERUSER RULES ---------------- #
    @staticmethod
    def _enforce_superuser_rules(actor: Staff, target: Staff, action: str):
        """
        Superuser rules:
        - Only the superuser can view/edit/delete their own record.
        - No one can change superuser `role` or `department`.
        """
        if actor.id != target.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot perform actions on another superuser."
            )

        if action in ["edit"]:
            # Block editing restricted fields
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The fields 'role' and 'department' for superuser cannot be edited."
            )

    # ---------------- ADMIN RULES ---------------- #
    @staticmethod
    def _enforce_admin_rules(actor: Staff, target: Staff, action: str):
        """
        Admin rules:
        - Superuser can view/edit/delete/create Admins.
        - Other staff roles cannot manage Admins.
        """
        if actor.role == StaffRole.SUPERUSER:
            return  # full rights on Admins

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superuser can manage admins."
        )

    # ---------------- CREATION RESTRICTIONS ---------------- #
    @staticmethod
    def ensure_single_superuser(db: Session, role: StaffRole, department: Department):
        """
        Prevent creation of multiple superusers.
        Both role=superuser and department=superuser must remain unique.
        """
        if role == StaffRole.SUPERUSER:
            existing = db.query(Staff).filter(Staff.role == StaffRole.SUPERUSER).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A superuser already exists."
                )

        if department == Department.SUPERUSER:
            existing = db.query(Staff).filter(Staff.department == Department.SUPERUSER).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A superuser department already exists."
                )
