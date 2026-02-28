from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ..config import get_settings
from ..services.auth_service import get_user_by_email
from ..models.users import RoleEnum
from ..dependencies import get_db

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _raise_401():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            _raise_401()
    except JWTError:
        _raise_401()

    user = get_user_by_email(email)
    if not user:
        _raise_401()
    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(role: RoleEnum):
    def _require(current_user=Depends(get_current_active_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user

    return _require
