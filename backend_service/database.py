import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend_service.config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW

# In Lambda, limit pool to 1 to avoid connection exhaustion across concurrent
# invocations.  Each Lambda instance gets its own process & pool.
_is_lambda = bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME'))
_pool_size = 1 if _is_lambda else DB_POOL_SIZE
_max_overflow = 2 if _is_lambda else DB_MAX_OVERFLOW

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=_pool_size,
    max_overflow=_max_overflow,
    pool_recycle=300,       # recycle stale connections every 5 min
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
