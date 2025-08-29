from functools import wraps
from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.auth import get_current_user

def permission_required(permission_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized"
                )
            
            # check if user has permission
            has_permission = any(p.name == permission_name for p in current_user.permissions)
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
