from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import sys

# 确保backend/app目录在Python路径中
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(BACKEND_DIR)

# 数据库目录设置 - 使用项目根目录下的data文件夹
DATABASE_DIR = os.path.join(PROJECT_DIR, 'data')

# 确保数据库目录存在
try:
    os.makedirs(DATABASE_DIR, exist_ok=True)
    print(f"[Database] Database directory: {DATABASE_DIR}")
except Exception as e:
    print(f"[Database] Warning: Could not create database directory: {e}")
    # 使用临时目录作为备用
    DATABASE_DIR = os.path.join(APP_DIR, 'data')
    os.makedirs(DATABASE_DIR, exist_ok=True)
    print(f"[Database] Using fallback directory: {DATABASE_DIR}")

# 数据库文件路径
DATABASE_FILE = os.path.join(DATABASE_DIR, 'career_guidance.db')

# 数据库连接URL
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# 创建SQLAlchemy引擎
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建声明基类
Base = declarative_base()

# 获取数据库会话的依赖函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 获取数据库文件路径
def get_database_file():
    return DATABASE_FILE

# 检查数据库文件是否存在
def check_database_exists():
    return os.path.exists(DATABASE_FILE)

# 获取数据库文件大小（字节）
def get_database_size():
    if os.path.exists(DATABASE_FILE):
        return os.path.getsize(DATABASE_FILE)
    return 0

# 创建所有表
def create_tables():
    """创建所有数据库表"""
    try:
        # 导入所有模型以确保它们被注册
        from . import models
        from . import models_user_profile
        from . import models_user_report
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print(f"[Database] All tables created successfully.")
        print(f"[Database] Database file: {DATABASE_FILE}")
        return True
    except Exception as e:
        print(f"[Database] Error creating tables: {e}")
        return False

# 删除所有表（谨慎使用）
def drop_tables():
    """删除所有数据库表"""
    try:
        Base.metadata.drop_all(bind=engine)
        print(f"[Database] All tables dropped.")
        return True
    except Exception as e:
        print(f"[Database] Error dropping tables: {e}")
        return False

# 初始化数据库（创建表并返回状态）
def init_database():
    """初始化数据库，返回数据库状态信息"""
    db_exists = check_database_exists()
    db_size = get_database_size()
    
    if not db_exists or db_size == 0:
        print(f"[Database] Creating new database...")
        create_tables()
        db_exists = check_database_exists()
        db_size = get_database_size()
    
    return {
        "database_exists": db_exists,
        "database_size": db_size,
        "database_file": DATABASE_FILE
    }
