from typing import Generator
from .database import SessionLocal


def get_db() -> Generator:
    """Dependency that yields a SQLAlchemy session and ensures it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
