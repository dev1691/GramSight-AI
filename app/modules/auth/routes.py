from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...schemas.auth import UserCreate, UserLogin, Token
from ...core.security import create_access_token
from ...services import auth_service
from ...models.users import RoleEnum

router = APIRouter()


@router.post("/register", response_model=Token)
def register(payload: UserCreate):
    try:
        role = RoleEnum(payload.role) if payload.role else RoleEnum.farmer
    except Exception:
        role = RoleEnum.farmer

    try:
        user = auth_service.create_user(email=payload.email, password=payload.password, role=role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(payload: UserLogin):
    user = auth_service.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
