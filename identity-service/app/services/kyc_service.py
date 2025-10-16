from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_model import User, UserStatus
from app.models.kyc_model import KYCVerification
from app.schemas.kyc_schema import KYCVerificationCreate
from app.utils.activity_logger import log_activity


class KYCService:
    # -------------------------
    # KYC Handling
    # -------------------------
    @staticmethod
    def submit_kyc(db: Session, user: User, kyc_in: KYCVerificationCreate, actor: User = None, request=None) -> KYCVerification:
        """Submit new KYC attempt for user (keeps history)."""
        try:
            kyc = KYCVerification(user_id=user.id, **kyc_in.dict())
            db.add(kyc)

            # Update user status
            user.status = UserStatus.PENDING_KYC
            db.commit()
            db.refresh(kyc)

            log_activity(
                db, actor or user, "kyc_submit_success", request=request,
                description=f"KYC submitted for user {user.username}"
            )

            return kyc
        except Exception as e:
            log_activity(
                db, actor or user, "kyc_submit_error", request=request,
                description=str(e)
            )
            raise

    @staticmethod
    def get_latest_kyc(user: User, db: Session, actor: User = None, request=None) -> KYCVerification | None:
        """Return most recent KYC record for a user."""
        try:
            if not user.kyc_verifications:
                log_activity(
                    db, actor or user, "kyc_get_none", request=request,
                    description=f"No KYC records found for user {user.username}"
                )
                return None

            latest = sorted(user.kyc_verifications, key=lambda k: k.date_created)[-1]

            log_activity(
                db, actor or user, "kyc_get_latest", request=request,
                description=f"Latest KYC retrieved for user {user.username}"
            )

            return latest
        except Exception as e:
            log_activity(
                db, actor or user, "kyc_get_error", request=request,
                description=str(e)
            )
            raise
