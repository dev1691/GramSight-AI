import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
MARKET_API_KEY = os.getenv('MARKET_API_KEY')

DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'gramsight_db')
DB_USER = os.getenv('DB_USER', 'gs_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'gs_pass')

SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable must be set and non-empty")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))

ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv('ALLOWED_ORIGINS', 'http://localhost:8080,http://localhost:3000').split(',')
    if o.strip()
]

# Sync DB URL for psycopg2
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Async DB URL for asyncpg
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Connection pool settings
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))

