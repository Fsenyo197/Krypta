from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone
from app.models.api_key_model import APIKey
from app.models.permission_model import Permission
from app.schemas.api_key_schema import APIKeyCreate, APIKeyUpdate


def create_api_key(db: Session, api_key_in: APIKeyCreate) -> APIKey:
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
    return api_key


def get_api_key(db: Session, api_key_id: UUID) -> APIKey:
    api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")
    return api_key


def list_api_keys(db: Session, user_id: UUID = None) -> list[APIKey]:
    query = db.query(APIKey)
    if user_id:
        query = query.filter(APIKey.user_id == user_id)
    return query.all()


def update_api_key(db: Session, api_key_id: UUID, api_key_in: APIKeyUpdate) -> APIKey:
    api_key = get_api_key(db, api_key_id)

    if api_key_in.is_active is not None:
        api_key.is_active = api_key_in.is_active
    if api_key_in.expires_at is not None:
        api_key.expires_at = api_key_in.expires_at
    if api_key_in.permissions is not None:
        perms = db.query(Permission).filter(Permission.id.in_(api_key_in.permissions)).all()
        api_key.permissions = perms

    api_key.date_updated = datetime.now(timezone.utc)()
    db.commit()
    db.refresh(api_key)
    return api_key


def delete_api_key(db: Session, api_key_id: UUID) -> None:
    api_key = get_api_key(db, api_key_id)
    db.delete(api_key)
    db.commit()
