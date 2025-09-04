from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.session_model import Session
from app.schemas.session_schema import SessionCreate, SessionUpdate, SessionResponse


class SessionService:
    @staticmethod
    def create_session(db: Session, session_in: SessionCreate) -> SessionResponse:
        """Create and persist a new user session."""
        session = Session(**session_in.dict())
        db.add(session)
        db.commit()
        db.refresh(session)
        return SessionResponse.from_orm(session)

    @staticmethod
    def invalidate_session(db: Session, refresh_token: str, user_id: str) -> None:
        """Invalidate a session by refresh token for a specific user."""
        session = (
            db.query(Session)
            .filter_by(user_id=user_id, refresh_token=refresh_token, is_valid=True)
            .first()
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or already invalidated",
            )
        session.is_valid = False
        db.commit()

    @staticmethod
    def validate_refresh_token(db: Session, refresh_token: str, user_id: str) -> Session:
        """Ensure refresh token exists, is valid, and not expired."""
        session = (
            db.query(Session)
            .filter_by(user_id=user_id, refresh_token=refresh_token, is_valid=True)
            .first()
        )
        if not session or session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        return session
