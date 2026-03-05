import os
import asyncio
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from backend_service.services.auth_service import get_user_by_email
from backend_service.models import RoleEnum
from backend_service.config import SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _raise_401():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            _raise_401()
    except JWTError:
        _raise_401()

    # Run the sync DB call in a thread to avoid blocking the event loop
    user = await asyncio.to_thread(get_user_by_email, email)
    if not user:
        _raise_401()
    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(role: RoleEnum):
    def _require(current_user=Depends(get_current_active_user)):
        if current_user.role != (role.value if hasattr(role, 'value') else role):
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user

    return _require
