from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from backend_service.services.auth_service import authenticate_user, create_user
from backend_service.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from backend_service.core.dependencies import get_current_active_user, require_role
from backend_service.models import RoleEnum

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = RoleEnum.farmer.value


class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/admin/users", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def admin_create_user(payload: UserCreate):
    user = create_user(payload.email, payload.password, role=payload.role)
    return {"id": str(user.id), "email": user.email, "role": user.role}


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_active_user)):
    return {"id": str(current_user.id), "email": current_user.email, "role": current_user.role}
