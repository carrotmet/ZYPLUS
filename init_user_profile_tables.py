# -*- coding: utf-8 -*-
"""
初始化用户画像相关数据表
"""

import sys
import os

# 添加backend到路径
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.chdir(backend_path)

from app.database import engine, Base
from app import models  # 导入原有模型以注册occupations表
from app import models_user_profile

print("=" * 60)
print("Initializing User Profile Tables")
print("=" * 60)

# 创建用户画像相关表
try:
    models_user_profile.Base.metadata.create_all(bind=engine)
    print("[OK] User profile tables created successfully!")
    print("\nCreated tables:")
    print("  - user_profiles")
    print("  - user_conversations")
    print("  - user_profile_logs")
    print("  - user_career_path_recommendations")
except Exception as e:
    print(f"[ERROR] Failed to create tables: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
