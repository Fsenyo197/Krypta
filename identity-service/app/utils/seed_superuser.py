from sqlalchemy.orm import Session
from app.models.user_model import User, UserStatus
from app.models.staff_model import Staff
from app.models.permission_model import Permission
from app.services.user_service import hash_password
import uuid

def seed_superuser(db: Session):
    SUPERUSER_EMAIL = "superuser@system.local"
    SUPERUSER_USERNAME = "superuser"

    # check if superuser already exists
    existing_user = db.query(User).filter(User.is_superuser == True).first()
    if existing_user:
        print("[*] Superuser already exists.")
        return existing_user

    # create user
    superuser = User(
        id=uuid.uuid4(),
        username=SUPERUSER_USERNAME,
        email=SUPERUSER_EMAIL,
        phone_number="0000000000",
        hashed_password=hash_password("SuperSecurePassword123!"),
        is_verified=True,
        status=UserStatus.ACTIVE,
        is_superuser=True
    )
    db.add(superuser)
    db.flush() 

    # create staff profile
    staff = Staff(
        user_id=superuser.id,
        department="IT",
        role="superuser"
    )
    db.add(staff)
    db.flush()

    # assign all permissions
    permissions = db.query(Permission).all()
    staff.permissions.extend(permissions)

    db.commit()
    print("[*] Superuser seeded successfully.")

    return superuser
