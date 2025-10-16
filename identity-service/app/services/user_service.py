from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import User, UserStatus
from app.schemas.user_schema import UserCreate, UserUpdate
from app.utils.activity_logger import log_activity 
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class UserService:
    # -------------------------
    # Authentication
    # -------------------------
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str, request=None) -> User:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            log_activity(db, None, "login_failed", request=request, description=f"Failed login attempt for {email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if user.status == UserStatus.SUSPENDED:
            log_activity(db, user, "login_blocked", request=request, description="Login blocked - account suspended")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")

        log_activity(db, user, "login_success", request=request, description=f"User {email} logged in")
        return user

    # -------------------------
    # CRUD: Create
    # -------------------------
    @staticmethod
    def create_user(db: Session, user_in: UserCreate, current_user: User = None, request=None) -> User:
        try:
            if getattr(user_in, "is_superuser", False):
                log_activity(db, current_user, "create_user_denied", request=request,
                             description="Attempt to create superuser")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create another superuser")

            if db.query(User).filter(User.username == user_in.username).first():
                log_activity(db, current_user, "create_user_failed", request=request,
                             description=f"Username {user_in.username} already taken")
                raise HTTPException(status_code=400, detail="Username already taken")

            if db.query(User).filter(User.email == user_in.email).first():
                log_activity(db, current_user, "create_user_failed", request=request,
                             description=f"Email {user_in.email} already registered")
                raise HTTPException(status_code=400, detail="Email already registered")

            user = User(
                username=user_in.username,
                email=user_in.email,
                phone_number=user_in.phone_number,
                hashed_password=hash_password(user_in.password),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            log_activity(db, user, "create_user_success", request=request,
                         description=f"User {user.username} created by {current_user.username if current_user else 'system'}")

            return user
        except HTTPException:
            raise  # re-raise after logging
        except Exception as e:
            log_activity(db, current_user, "create_user_error", request=request, description=str(e))
            raise


    # -------------------------
    # CRUD: Update
    # -------------------------
    @staticmethod
    def update_user(db: Session, user: User, user_in: UserUpdate, current_user: User, request=None) -> User:
        try:
            if user.is_superuser and user.id != current_user.id:
                log_activity(db, current_user, "update_user_denied", request=request,
                             description="Attempt to edit another superuser")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the superuser can edit their own account"
                )

            # --- Uniqueness checks ---
            if user_in.username and user_in.username != user.username:
                if db.query(User).filter(User.username == user_in.username).first():
                    log_activity(db, current_user, "update_user_failed", request=request,
                                 description=f"Username {user_in.username} already taken")
                    raise HTTPException(status_code=400, detail="Username already taken")

            if user_in.email and user_in.email != user.email:
                if db.query(User).filter(User.email == user_in.email).first():
                    log_activity(db, current_user, "update_user_failed", request=request,
                                 description=f"Email {user_in.email} already registered")
                    raise HTTPException(status_code=400, detail="Email already registered")

            if user_in.phone_number and user_in.phone_number != user.phone_number:
                if db.query(User).filter(User.phone_number == user_in.phone_number).first():
                    log_activity(db, current_user, "update_user_failed", request=request,
                                 description=f"Phone {user_in.phone_number} already registered")
                    raise HTTPException(status_code=400, detail="Phone number already registered")

            if user_in.password:
                user.hashed_password = hash_password(user_in.password)

            if user_in.is_verified is not None:
                user.is_verified = user_in.is_verified

            if user_in.status is not None:
                user.status = user_in.status

            if user_in.twofa_secret is not None:
                user.twofa_secret = user_in.twofa_secret

            db.commit()
            db.refresh(user)
            return user

            log_activity(db, user, "update_user_success", request=request,
                         description=f"User {user.username} updated by {current_user.username}")

            return user
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            log_activity(db, current_user, "update_user_error", request=request, description=str(e))
            raise


    # -------------------------
    # CRUD: Read
    # -------------------------
    @staticmethod
    def get_user_by_id(db: Session, user_id: int, current_user: User, request=None) -> User:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                log_activity(db, current_user, "get_user_failed", request=request,
                             description=f"User {user_id} not found")
                raise HTTPException(status_code=404, detail="User not found")

            if user.is_superuser and user.id != current_user.id:
                log_activity(db, current_user, "get_user_denied", request=request,
                             description=f"Attempt to view superuser {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Superuser cannot be viewed by other users"
                )

            log_activity(db, current_user, "get_user_success", request=request,
                         description=f"User {user.username} (id={user.id}) retrieved by {current_user.username}")
            return user
        except HTTPException:
            raise
        except Exception as e:
            log_activity(db, current_user, "get_user_error", request=request, description=str(e))
            raise HTTPException(status_code=500, detail="Error retrieving user")

    @staticmethod
    def list_users(db: Session, current_user: User = None, skip: int = 0, limit: int = 100, request=None) -> list[User]:
        try:
            users = (
                db.query(User)
                .filter(User.is_superuser == False) 
                .offset(skip)
                .limit(limit)
                .all()
            )
            log_activity(db, current_user, "list_users_success", request=request,
                         description=f"{len(users)} users retrieved by {current_user.username if current_user else 'system'}")
            return users
        except Exception as e:
            log_activity(db, current_user, "list_users_error", request=request, description=str(e))
            raise HTTPException(status_code=500, detail="Error retrieving users")


    # -------------------------
    # CRUD: Delete
    # -------------------------
    @staticmethod
    def delete_user(db: Session, user: User, current_user: User, request=None) -> None:
        try:
            if user.is_superuser and user.id != current_user.id:
                log_activity(db, current_user, "delete_user_denied", request=request,
                             description="Attempt to delete superuser")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Superuser cannot be deleted by others")

            db.delete(user)
            db.commit()

            log_activity(db, user, "delete_user_success", request=request,
                         description=f"User {user.username} deleted by {current_user.username}")
        except HTTPException:
            raise
        except Exception as e:
            log_activity(db, current_user, "delete_user_error", request=request, description=str(e))
            raise
