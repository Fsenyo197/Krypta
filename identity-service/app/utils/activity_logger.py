from fastapi import Request
from sqlalchemy.orm import Session
from app.models.activity_log_model import ActivityLog
from app.models.user_model import User

# Activity descriptions (centralized)
ACTIVITY_DESCRIPTIONS = {
    "login": "User {username} logged in successfully.",
    "login_failed": "Failed login attempt for username {username}.",
    "logout": "User {username} logged out.",
    "staff:promote": "Admin {admin} promoted user {user} to staff.",
    "staff:demote": "Admin {admin} removed staff role from user {user}.",
    "permission:assign": "Permission '{permission}' granted to user {user}.",
    "permission:revoke": "Permission '{permission}' revoked from user {user}.",
}


def log_activity(
    db: Session,
    user: User,
    activity_type: str,
    request: Request = None,
    **kwargs,
) -> ActivityLog:
    """
    Logs a user activity into the ActivityLog table.
    """

    # Build description from template
    description_template = ACTIVITY_DESCRIPTIONS.get(activity_type, "{activity_type}")
    description = description_template.format(
        username=getattr(user, "username", "unknown"),
        activity_type=activity_type,
        **kwargs,
    )

    # Extract request metadata (if available)
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    # Create log entry
    log = ActivityLog(
        user_id=user.id,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log
