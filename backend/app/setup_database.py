#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Setup Script - 数据库建表脚本

This script creates all database tables for the Career Guidance Platform.
运行此脚本可快速创建数据库所有数据表。

Usage:
    python setup_database.py [--force]

Options:
    --force    Force recreate all tables (WARNING: will delete existing data)
"""

import sys
import os

# 确保backend/app目录在Python路径中
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(BACKEND_DIR)

# 添加到Python路径
sys.path.insert(0, BACKEND_DIR)

# 导入数据库模块
from app.database import engine, Base, check_database_exists, get_database_file
from app import models
from app import models_user_profile


def create_all_tables():
    """创建所有数据库表"""
    print("=" * 60)
    print("           Career Planning Platform - Database Setup")
    print("=" * 60)
    print()
    
    # 检查数据库是否存在
    db_exists = check_database_exists()
    db_file = get_database_file()
    
    print(f"[INFO] Database file: {db_file}")
    print(f"[INFO] Database exists: {db_exists}")
    print()
    
    try:
        # 导入所有模型
        print("[INFO] Importing database models...")
        from app.models import (
            Discipline, MajorCategory, Major, 
            Occupation, MajorOccupation, CareerPath,
            PersonalExperience, ExperienceShare
        )
        from app.models_user_profile import (
            UserProfile, UserConversation,
            UserProfileLog, UserCareerPathRecommendation
        )
        print("[INFO] Models imported successfully.")
        print()
        print("[INFO] User Profile module loaded.")
        print()
        
        # 创建所有表
        print("[INFO] Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # 列出所有创建的表
        print("[INFO] Tables created:")
        for table in Base.metadata.tables.keys():
            print(f"       - {table}")
        
        print()
        print("=" * 60)
        print("              Database Setup Complete!")
        print("=" * 60)
        print()
        print(f"[INFO] Database location: {db_file}")
        print()
        print("[NEXT STEPS]:")
        print("  1. Start backend: python -m uvicorn app.main:app --reload")
        print("  2. Init sample data: POST /api/init-data")
        print("  3. API docs: http://localhost:8000/docs")
        print()
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create database tables: {e}")
        import traceback
        traceback.print_exc()
        return False


def drop_all_tables():
    """删除所有数据库表（谨慎使用）"""
    print("[WARNING] Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("[INFO] All tables dropped successfully.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to drop tables: {e}")
        return False


def main():
    """主函数"""
    # 检查是否强制重建
    force = "--force" in sys.argv
    
    if force:
        print("[WARNING] Force mode enabled - will recreate all tables")
        print()
        db_exists = check_database_exists()
        if db_exists:
            confirm = input("This will DELETE all existing data! Continue? (y/n): ")
            if confirm.lower() != 'y':
                print("[INFO] Cancelled.")
                return
            drop_all_tables()
    
    success = create_all_tables()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
