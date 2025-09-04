from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.kyc_schema import KYCVerificationCreate
from app.services.kyc_service import KYCService
from app.db import get_db
from app.models.user_model import User
from app.utils.current_user import get_current_user


kyc_router = APIRouter(prefix="/users", tags=["Users"])


# -------------------------
# Submit KYC for logged-in user
# -------------------------
@kyc_router.post("/me/kyc", response_model=dict)
def submit_kyc(
    kyc_in: KYCVerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kyc = KYCService.submit_kyc(db, current_user, kyc_in)
    return {"detail": "KYC submitted successfully", "kyc_id": str(kyc.id)}


# -------------------------
# Get latest KYC for logged-in user
# -------------------------
@kyc_router.get("/me/kyc/latest", response_model=dict)
def get_latest_kyc(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kyc = KYCService.get_latest_kyc(current_user)
    if not kyc:
        raise HTTPException(status_code=404, detail="No KYC record found")
    return {"kyc_id": str(kyc.id), "status": kyc.status.value, "submitted_at": kyc.date_created}
