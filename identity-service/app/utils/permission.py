from functools import wraps
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.models.staff_model import Staff
from app.utils.current_user import get_current_user
from app.db import get_db

def permission_required(permission_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db),
            **kwargs
        ):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized"
                )

            # fetch staff record linked to the user
            staff = db.query(Staff).filter(Staff.user_id == current_user.id).first()
            if not staff:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a staff member"
                )

            # check staff permissions
            has_permission = any(p.name == permission_name for p in staff.permissions)
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission_name}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
