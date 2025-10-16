from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.schemas.api_key_schema import APIKeyResponse, APIKeyCreate, APIKeyUpdate
from app.services import api_key_service
from app.db import get_db
from app.models.user_model import User
from app.utils.current_user import get_current_user
from app.utils.permission import permission_required

api_key_router = APIRouter(prefix="/api-keys", tags=["API Keys"])


# -------------------------
# Create API Key
# -------------------------
@api_key_router.post("/", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
@permission_required("apikey:create")
def create_api_key(
    api_key_in: APIKeyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api_key = api_key_service.create_api_key(db, api_key_in)
    return api_key


# -------------------------
# Get API Key by ID
# -------------------------
@api_key_router.get("/{api_key_id}", response_model=APIKeyResponse)
@permission_required("apikey:read")
def get_api_key(
    api_key_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api_key = api_key_service.get_api_key(db, api_key_id)
    return api_key


# -------------------------
# List API Keys
# -------------------------
@api_key_router.get("/", response_model=List[APIKeyResponse])
@permission_required("apikey:list")
def list_api_keys(
    user_id: UUID = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api_keys = api_key_service.list_api_keys(db, user_id)
    return api_keys


# -------------------------
# Update API Key
# -------------------------
@api_key_router.put("/{api_key_id}", response_model=APIKeyResponse)
@permission_required("apikey:update")
def update_api_key(
    api_key_id: UUID,
    api_key_in: APIKeyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api_key = api_key_service.update_api_key(db, api_key_id, api_key_in)
    return api_key


# -------------------------
# Delete API Key
# -------------------------
@api_key_router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
@permission_required("apikey:delete")
def delete_api_key(
    api_key_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api_key_service.delete_api_key(db, api_key_id)
    return {"detail": "API Key deleted successfully"}
