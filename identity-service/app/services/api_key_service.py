from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone
from app.models.api_key_model import APIKey
from app.models.permission_model import Permission
from app.schemas.api_key_schema import APIKeyCreate, APIKeyUpdate
from app.utils.activity_logger import log_activity


def create_api_key(db: Session, api_key_in: APIKeyCreate, actor=None, request=None) -> APIKey:
    try:
        api_key = APIKey(
            user_id=api_key_in.user_id,
            key_hash=api_key_in.key_hash,
            secret=api_key_in.secret,
            is_active=api_key_in.is_active,
            expires_at=api_key_in.expires_at,
        )

        if api_key_in.permissions:
            perms = db.query(Permission).filter(Permission.id.in_(api_key_in.permissions)).all()
            api_key.permissions = perms

        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        log_activity(db, actor, "api_key_create_success", request=request,
                     description=f"API key created for user_id={api_key_in.user_id}")
        return api_key
    except Exception as e:
        log_activity(db, actor, "api_key_create_error", request=request, description=str(e))
        raise


def get_api_key(db: Session, api_key_id: UUID, actor=None, request=None) -> APIKey:
    api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
    if not api_key:
        log_activity(db, actor, "api_key_get_not_found", request=request,
                     description=f"API key {api_key_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")

    log_activity(db, actor, "api_key_get_success", request=request,
                 description=f"API key {api_key_id} retrieved")
    return api_key


def list_api_keys(db: Session, user_id: UUID = None, actor=None, request=None) -> list[APIKey]:
    query = db.query(APIKey)
    if user_id:
        query = query.filter(APIKey.user_id == user_id)
    results = query.all()

    log_activity(db, actor, "api_key_list", request=request,
                 description=f"Listed API keys (user_id={user_id if user_id else 'all'})")
    return results


def update_api_key(db: Session, api_key_id: UUID, api_key_in: APIKeyUpdate, actor=None, request=None) -> APIKey:
    try:
        api_key = get_api_key(db, api_key_id, actor=actor, request=request)

        if api_key_in.is_active is not None:
            api_key.is_active = api_key_in.is_active
        if api_key_in.expires_at is not None:
            api_key.expires_at = api_key_in.expires_at
        if api_key_in.permissions is not None:
            perms = db.query(Permission).filter(Permission.id.in_(api_key_in.permissions)).all()
            api_key.permissions = perms

        api_key.date_updated = datetime.now(timezone.utc)
        db.commit()
        db.refresh(api_key)

        log_activity(db, actor, "api_key_update_success", request=request,
                     description=f"API key {api_key_id} updated")
        return api_key
    except Exception as e:
        log_activity(db, actor, "api_key_update_error", request=request, description=str(e))
        raise


def delete_api_key(db: Session, api_key_id: UUID, actor=None, request=None) -> None:
    try:
        api_key = get_api_key(db, api_key_id, actor=actor, request=request)
        db.delete(api_key)
        db.commit()

        log_activity(db, actor, "api_key_delete_success", request=request,
                     description=f"API key {api_key_id} deleted")
    except Exception as e:
        log_activity(db, actor, "api_key_delete_error", request=request, description=str(e))
        raise
