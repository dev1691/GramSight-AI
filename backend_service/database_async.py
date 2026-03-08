import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend_service.config import DATABASE_URL_ASYNC, DB_POOL_SIZE, DB_MAX_OVERFLOW

_is_lambda = bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME'))
_pool_size = 1 if _is_lambda else DB_POOL_SIZE
_max_overflow = 2 if _is_lambda else DB_MAX_OVERFLOW

async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,
    future=True,
    pool_size=_pool_size,
    max_overflow=_max_overflow,
    pool_recycle=300,
)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
