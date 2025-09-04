from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.schemas.api_key_schema import APIKeyResponse, APIKeyCreate, APIKeyUpdate
from app.services import api_key_service
from app.db import get_db

api_key_router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@api_key_router.post("/api_key", response_model=APIKeyResponse, status_code=201)
def create_api_key(api_key_in: APIKeyCreate, db: Session = Depends(get_db)):
    return api_key_service.create_api_key(db, api_key_in)


@api_key_router.get("api_key/{api_key_id}", response_model=APIKeyResponse)
def get_api_key(api_key_id: UUID, db: Session = Depends(get_db)):
    return api_key_service.get_api_key(db, api_key_id)


@api_key_router.get("/", response_model=List[APIKeyResponse])
def list_api_keys(user_id: UUID = None, db: Session = Depends(get_db)):
    return api_key_service.list_api_keys(db, user_id)


@api_key_router.put("/{api_key_id}", response_model=APIKeyResponse)
def update_api_key(api_key_id: UUID, api_key_in: APIKeyUpdate, db: Session = Depends(get_db)):
    return api_key_service.update_api_key(db, api_key_id, api_key_in)


@api_key_router.delete("/{api_key_id}", status_code=204)
def delete_api_key(api_key_id: UUID, db: Session = Depends(get_db)):
    api_key_service.delete_api_key(db, api_key_id)
    return {"detail": "API Key deleted successfully"}
