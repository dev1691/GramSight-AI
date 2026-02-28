import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


def _get_bool(key: str, default: bool = False) -> bool:
    v = os.getenv(key)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    secret_key: str = ""
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    access_token_expire_minutes: int = 60
    openweather_api_key: Optional[str] = None
    market_api_key: Optional[str] = None

    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[str] = None
    use_docker_db: bool = False


def get_settings() -> Settings:
    s = Settings()
    s.database_url = os.getenv("DATABASE_URL")
    s.redis_url = os.getenv("REDIS_URL")
    s.secret_key = os.getenv("SECRET_KEY", "")
    allowed = os.getenv("ALLOWED_ORIGINS", "*")
    s.allowed_origins = [o.strip() for o in allowed.split(",")] if allowed else ["*"]
    s.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    s.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
    s.market_api_key = os.getenv("MARKET_API_KEY")

    s.postgres_user = os.getenv("POSTGRES_USER")
    s.postgres_password = os.getenv("POSTGRES_PASSWORD")
    s.postgres_db = os.getenv("POSTGRES_DB")
    s.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    s.postgres_port = os.getenv("POSTGRES_PORT", "5432")
    s.use_docker_db = _get_bool("USE_DOCKER_DB", False)

    # Optionally assemble DATABASE_URL from POSTGRES_* env vars (useful for docker-compose)
    if not s.database_url and s.use_docker_db:
        if s.postgres_user and s.postgres_password and s.postgres_db:
            s.database_url = f"postgresql+psycopg2://{s.postgres_user}:{s.postgres_password}@{s.postgres_host}:{s.postgres_port}/{s.postgres_db}"

    if not s.database_url:
        raise RuntimeError("DATABASE_URL is not set. Set it in .env or provide POSTGRES_* with USE_DOCKER_DB=true")

    if not s.secret_key:
        raise RuntimeError("SECRET_KEY is not set. Set it in .env for security")

    return s
