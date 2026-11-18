from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator

from src.api.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from src.data.history import (
    create_user,
    delete_user,
    get_user_by_username,
    list_users,
    update_password,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def _strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña nueva debe tener al menos 8 caracteres.")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=201)
def register(req: RegisterRequest) -> UserResponse:
    if get_user_by_username(req.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")
    user = create_user(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
    )
    return UserResponse(**user)


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    user = get_user_by_username(form.username)
    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")
    token = create_access_token(username=user["username"], role=user["role"])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=user["username"],
        role=user["role"],
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    user = get_user_by_username(current_user["username"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return UserResponse(**user)


@router.put("/me/password")
def change_password(
    req: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    user = get_user_by_username(current_user["username"])
    if not user or not verify_password(req.current_password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta.")
    update_password(current_user["username"], hash_password(req.new_password))
    return {"updated": True, "message": "Contraseña actualizada correctamente."}


@router.get("/users", response_model=list[UserResponse])
def get_all_users(admin: dict = Depends(require_admin)) -> list[UserResponse]:
    return [UserResponse(**u) for u in list_users()]


@router.delete("/users/{user_id}")
def remove_user(user_id: int, admin: dict = Depends(require_admin)) -> dict:
    if not delete_user(user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {"deleted": True}
