# -*- coding: utf-8 -*-
"""
用户画像模块完整验证报告
"""

import os
import sys

print("=" * 70)
print("用户画像模块验证报告")
print("=" * 70)

# 1. 检查文件结构
print("\n[1] 文件结构检查")
print("-" * 50)

files_to_check = [
    ("backend/app/models_user_profile.py", "数据模型"),
    ("backend/app/schemas_user_profile.py", "Pydantic Schema"),
    ("backend/app/crud_user_profile.py", "CRUD操作"),
    ("backend/app/api_user_profile.py", "API路由"),
    ("backend/app/services/rag_service.py", "RAG服务"),
    ("backend/app/services/__init__.py", "服务模块初始化"),
    ("user-profile.html", "前端页面"),
    ("user-profile.js", "前端逻辑"),
]

all_files_exist = True
for filepath, desc in files_to_check:
    exists = os.path.exists(filepath)
    status = "OK" if exists else "MISSING"
    print(f"  [{status}] {desc}: {filepath}")
    if not exists:
        all_files_exist = False

# 2. 数据库检查
print("\n[2] 数据库表检查")
print("-" * 50)

try:
    import sqlite3
    db_path = 'data/career_guidance.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        user_profile_tables = [
            'user_profiles',
            'user_conversations', 
            'user_profile_logs',
            'user_career_path_recommendations'
        ]
        
        for table in user_profile_tables:
            status = "OK" if table in tables else "MISSING"
            print(f"  [{status}] {table}")
        
        conn.close()
    else:
        print(f"  [ERROR] Database not found: {db_path}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 3. 依赖检查
print("\n[3] 依赖检查")
print("-" * 50)

dependencies = [
    ("fastapi", "FastAPI"),
    ("sqlalchemy", "SQLAlchemy"),
    ("pydantic", "Pydantic"),
    ("lazyllm", "LazyLLM"),
]

for module, name in dependencies:
    try:
        __import__(module)
        print(f"  [OK] {name}")
    except ImportError:
        print(f"  [MISSING] {name}")

# 4. LazyLLM详细检查
print("\n[4] LazyLLM服务检查")
print("-" * 50)

try:
    import lazyllm
    print(f"  Version: {lazyllm.__version__}")
    
    # 检查关键组件
    from lazyllm import OnlineChatModule
    print(f"  [OK] OnlineChatModule available")
    
    # 尝试初始化服务
    print("\n  Testing RAG service initialization...")
    sys.path.insert(0, 'backend')
    from app.services.rag_service import get_rag_service
    
    rag = get_rag_service()
    print(f"  [OK] RAG service initialized")
    print(f"  [OK] Loaded {len(rag.skill_docs)} skill documents")
    
    # 测试处理消息
    print("\n  Testing message processing...")
    result = rag.process_message(
        user_message="我对编程很感兴趣",
        user_profile={},
        conversation_history=[]
    )
    print(f"  [OK] Intent: {result['intent']}")
    print(f"  [OK] Reply: {result['reply'][:50]}...")
    print(f"  [OK] Extracted: {result['extracted_info']}")
    
except Exception as e:
    print(f"  [ERROR] {e}")
    import traceback
    traceback.print_exc()

# 5. API路由检查
print("\n[5] API路由检查")
print("-" * 50)

try:
    sys.path.insert(0, 'backend')
    from app.api_user_profile import router
    
    routes = [(r.path, r.methods) for r in router.routes]
    print(f"  [OK] Total routes: {len(routes)}")
    
    expected_routes = [
        "/{user_id}",
        "/{user_id}/chat",
        "/{user_id}/completeness",
        "/{user_id}/analyze",
        "/{user_id}/visualization"
    ]
    
    for route in expected_routes:
        found = any(route == r[0] for r in routes)
        status = "OK" if found else "MISSING"
        print(f"  [{status}] {route}")
        
except Exception as e:
    print(f"  [ERROR] {e}")

# 6. 总结
print("\n" + "=" * 70)
print("验证完成")
print("=" * 70)
print("""
启动服务:
  cd backend
  python -m uvicorn app.main:app --reload --port 8000

访问页面:
  打开 user-profile.html

API文档:
  http://localhost:8000/docs
""")
