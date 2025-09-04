from sqlalchemy.orm import Session
from app.models.user_model import User, UserStatus
from app.models.kyc_model import KYCVerification
from app.schemas.kyc_schema import KYCVerificationCreate



class KYCService:
    # -------------------------
    # KYC Handling
    # -------------------------
    @staticmethod
    def submit_kyc(db: Session, user: User, kyc_in: KYCVerificationCreate) -> KYCVerification:
        """Submit new KYC attempt for user (keeps history)."""
        kyc = KYCVerification(user_id=user.id, **kyc_in.dict())
        db.add(kyc)

        # Update user status
        user.status = UserStatus.PENDING_KYC
        db.commit()
        db.refresh(kyc)
        return kyc

    @staticmethod
    def get_latest_kyc(user: User) -> KYCVerification | None:
        """Return most recent KYC record for a user."""
        if not user.kyc_verifications:
            return None
        return sorted(user.kyc_verifications, key=lambda k: k.date_created)[-1]
