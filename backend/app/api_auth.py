# -*- coding: utf-8 -*-
"""
用户认证模块 - API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import hashlib
import secrets

from . import database, models, schemas

# 创建路由
router = APIRouter(prefix="/api/auth", tags=["用户认证"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    """生成登录令牌"""
    return secrets.token_urlsafe(32)


def generate_user_profile_id() -> str:
    """生成用户画像ID"""
    return 'user_' + secrets.token_urlsafe(16)


@router.post("/register", response_model=schemas.ResponseModel)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户画像ID
    user_profile_id = generate_user_profile_id()
    
    # 创建新用户
    new_user = models.User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        email=user_data.email,
        phone=user_data.phone,
        nickname=user_data.nickname or user_data.username,
        user_profile_id=user_profile_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return schemas.ResponseModel(
        data={
            "user_id": new_user.id,
            "username": new_user.username,
            "user_profile_id": user_profile_id,
            "message": "注册成功"
        }
    )


@router.post("/login", response_model=schemas.ResponseModel)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(models.User).filter(models.User.username == login_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if user.password_hash != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查用户状态
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 生成token
    token = generate_token()
    
    # 确保用户有画像ID
    if not user.user_profile_id:
        user.user_profile_id = generate_user_profile_id()
        db.commit()
    
    return schemas.ResponseModel(
        data={
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "user_profile_id": user.user_profile_id,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "user_profile_id": user.user_profile_id,
            "message": "登录成功"
        }
    )


@router.get("/profile", response_model=schemas.ResponseModel)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return schemas.ResponseModel(
        data={
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "user_profile_id": user.user_profile_id
            }
        }
    )


@router.get("/check-username")
def check_username(username: str, db: Session = Depends(get_db)):
    """检查用户名是否可用"""
    existing = db.query(models.User).filter(models.User.username == username).first()
    return {"available": existing is None}
