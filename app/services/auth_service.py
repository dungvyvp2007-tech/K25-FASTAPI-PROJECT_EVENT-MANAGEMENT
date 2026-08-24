from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from models.user import User
from schemas.auth import LoginRequest, RefreshRequest, RegisterRequest


def register_user(db: Session, payload: RegisterRequest) -> dict:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email đã được sử dụng")
    db.add(
        User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
        )
    )
    db.commit()
    return {"message": "Đăng ký tài khoản thành công"}


def login_user(db: Session, payload: LoginRequest) -> dict:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401, detail="Email hoặc mật khẩu không chính xác"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    return {
        "message": "Đăng nhập thành công",
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
    }


def refresh_access_token(db: Session, payload: RefreshRequest) -> dict:
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh" or not db.get(User, int(data["sub"])):
            raise ValueError()
    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=401, detail="Refresh token không hợp lệ hoặc đã hết hạn"
        )
    return {
        "message": "Cấp lại token thành công",
        "access_token": create_access_token(data["sub"]),
        "refresh_token": create_refresh_token(data["sub"]),
    }
