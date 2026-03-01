from typing import Optional
from sqlalchemy.orm import Session
from backend_service.database import SessionLocal
from backend_service.models import User, RoleEnum
from backend_service.core.security import get_password_hash, verify_password


def get_user_by_email(email: str) -> Optional[User]:
    db: Session = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def create_user(email: str, password: str, role: RoleEnum = RoleEnum.farmer) -> User:
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("User already exists")

        user = User(email=email, hashed_password=get_password_hash(password), role=role.value if hasattr(role, 'value') else role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def authenticate_user(email: str, password: str) -> Optional[User]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
