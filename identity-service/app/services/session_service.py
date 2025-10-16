from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.session_model import Session as UserSession
from app.schemas.session_schema import SessionCreate, SessionUpdate, SessionResponse
from app.utils.activity_logger import log_activity


class SessionService:
    @staticmethod
    def create_session(db: Session, session_in: SessionCreate, actor=None, request=None) -> SessionResponse:
        """Create and persist a new user session."""
        try:
            session = UserSession(**session_in.dict())
            db.add(session)
            db.commit()
            db.refresh(session)

            log_activity(
                db, actor, "session_create_success", request=request,
                description=f"Session created for user_id={session.user_id}"
            )

            return SessionResponse.from_orm(session)
        except Exception as e:
            log_activity(
                db, actor, "session_create_error", request=request,
                description=str(e)
            )
            raise

    @staticmethod
    def invalidate_session(db: Session, refresh_token: str, user_id: str, actor=None, request=None) -> None:
        """Invalidate a session by refresh token for a specific user."""
        session = (
            db.query(UserSession)
            .filter_by(user_id=user_id, refresh_token=refresh_token, is_valid=True)
            .first()
        )
        if not session:
            log_activity(
                db, actor, "session_invalidate_failed", request=request,
                description=f"No active session found for user_id={user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or already invalidated",
            )

        session.is_valid = False
        db.commit()

        log_activity(
            db, actor, "session_invalidate_success", request=request,
            description=f"Session invalidated for user_id={user_id}"
        )

    @staticmethod
    def validate_refresh_token(db: Session, refresh_token: str, user_id: str, actor=None, request=None) -> UserSession:
        """Ensure refresh token exists, is valid, and not expired."""
        session = (
            db.query(UserSession)
            .filter_by(user_id=user_id, refresh_token=refresh_token, is_valid=True)
            .first()
        )
        if not session:
            log_activity(
                db, actor, "session_validate_failed", request=request,
                description=f"Invalid refresh token for user_id={user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        if session.expires_at < datetime.now(timezone.utc):
            log_activity(
                db, actor, "session_validate_failed", request=request,
                description=f"Expired refresh token for user_id={user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Optional: log success, depending on verbosity preference
        log_activity(
            db, actor, "session_validate_success", request=request,
            description=f"Valid refresh token for user_id={user_id}"
        )

        return session
