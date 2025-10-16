from fastapi import Request
from sqlalchemy.orm import Session
from app.models.activity_log_model import ActivityLog
from app.models.user_model import User
from app.services.restriction_service import RestrictionService
from sqlalchemy.exc import SQLAlchemyError


def log_activity(
    db: Session,
    target_user: User = None,
    activity_type: str = None,
    request: Request = None,
    current_user: User = None,
    **kwargs,
) -> ActivityLog:
    """
    Logs a user activity into the ActivityLog table.
    Restrictions (e.g., superuser logs) are enforced centrally via RestrictionService.
    """

    # Enforce restrictions (only if both users provided)
    if current_user and target_user:
        RestrictionService.enforce(
            current_user.staff_profile,
            target_user.staff_profile,
            action="view_logs",
        )

    # Extract request metadata (if available)
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    # Create log entry
    log = ActivityLog(
        user_id=current_user.id if current_user else None,
        activity_type=activity_type,
        ip_address=ip_address,
        user_agent=user_agent,
        **kwargs,
    )

    try:
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except SQLAlchemyError as e:
        db.rollback()
        raise e
