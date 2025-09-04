from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import User, UserStatus
from app.schemas.user_schema import UserCreate, UserUpdate
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
    def authenticate_user(db: Session, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if user.status == UserStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account suspended"
            )

        return user

    # -------------------------
    # CRUD: Create
    # -------------------------
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        # Check for duplicates
        if db.query(User).filter(User.username == user_in.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if db.query(User).filter(User.phone_number == user_in.phone_number).first():
            raise HTTPException(status_code=400, detail="Phone number already registered")

        user = User(
            username=user_in.username,
            email=user_in.email,
            phone_number=user_in.phone_number,
            hashed_password=hash_password(user_in.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    # -------------------------
    # CRUD: Update
    # -------------------------
    @staticmethod
    def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
        if user_in.username and user_in.username != user.username:
            if db.query(User).filter(User.username == user_in.username).first():
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = user_in.username

        if user_in.email and user_in.email != user.email:
            if db.query(User).filter(User.email == user_in.email).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = user_in.email

        if user_in.phone_number and user_in.phone_number != user.phone_number:
            if db.query(User).filter(User.phone_number == user_in.phone_number).first():
                raise HTTPException(status_code=400, detail="Phone number already registered")
            user.phone_number = user_in.phone_number

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

    # -------------------------
    # CRUD: Read
    # -------------------------
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).offset(skip).limit(limit).all()

    # -------------------------
    # CRUD: Delete
    # -------------------------
    @staticmethod
    def delete_user(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()
