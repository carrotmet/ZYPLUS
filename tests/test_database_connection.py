#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
用于排查数据库连接问题
"""

import sys
import os

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

def test_basic_imports():
    """测试基础模块导入"""
    print("=" * 60)
    print("测试 1: 基础模块导入")
    print("=" * 60)
    
    try:
        from app.database import engine, SessionLocal, DATABASE_FILE, DATABASE_URL
        print(f"✅ database 模块导入成功")
        print(f"   数据库文件: {DATABASE_FILE}")
        print(f"   数据库URL: {DATABASE_URL}")
        print(f"   文件存在: {os.path.exists(DATABASE_FILE)}")
        if os.path.exists(DATABASE_FILE):
            print(f"   文件大小: {os.path.getsize(DATABASE_FILE)} bytes")
        return True
    except Exception as e:
        print(f"❌ database 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models_import():
    """测试模型模块导入"""
    print("\n" + "=" * 60)
    print("测试 2: 模型模块导入")
    print("=" * 60)
    
    models_to_test = [
        ('app.models', '基础模型'),
        ('app.models_user_profile', '用户画像模型'),
        ('app.models_user_report', '用户报告模型'),
    ]
    
    all_success = True
    for module_name, desc in models_to_test:
        try:
            __import__(module_name)
            print(f"✅ {desc} ({module_name}) 导入成功")
        except Exception as e:
            print(f"❌ {desc} ({module_name}) 导入失败: {e}")
            all_success = False
    
    return all_success

def test_database_session():
    """测试数据库会话创建"""
    print("\n" + "=" * 60)
    print("测试 3: 数据库会话创建")
    print("=" * 60)
    
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        print("✅ 数据库会话创建成功")
        
        # 测试简单查询
        try:
            result = db.execute("SELECT 1")
            print(f"✅ 简单查询测试成功: {result.scalar()}")
        except Exception as e:
            print(f"❌ 简单查询测试失败: {e}")
        
        db.close()
        print("✅ 数据库会话关闭成功")
        return True
    except Exception as e:
        print(f"❌ 数据库会话创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crud_operations():
    """测试 CRUD 操作"""
    print("\n" + "=" * 60)
    print("测试 4: CRUD 操作")
    print("=" * 60)
    
    try:
        from app.database import SessionLocal
        from app import crud
        
        db = SessionLocal()
        
        # 测试学科查询
        try:
            disciplines = crud.get_disciplines(db)
            print(f"✅ 学科查询成功: {len(disciplines)} 个学科")
            if disciplines:
                print(f"   第一个学科: {disciplines[0].name}")
        except Exception as e:
            print(f"❌ 学科查询失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试专业查询
        try:
            majors = crud.get_majors(db)
            print(f"✅ 专业查询成功: {len(majors)} 个专业")
        except Exception as e:
            print(f"❌ 专业查询失败: {e}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ CRUD 操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_table_structure():
    """测试表结构"""
    print("\n" + "=" * 60)
    print("测试 5: 数据库表结构")
    print("=" * 60)
    
    try:
        from app.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"✅ 数据库表查询成功: {len(tables)} 个表")
        for table in tables:
            print(f"   - {table}")
        
        # 检查关键表
        required_tables = [
            'disciplines', 'major_categories', 'majors',
            'occupations', 'career_paths',
            'users', 'user_profiles', 'user_conversations',
            'user_reports', 'generation_tasks'
        ]
        
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"⚠️ 缺失的表: {missing}")
        else:
            print("✅ 所有关键表都存在")
        
        return True
    except Exception as e:
        print(f"❌ 表结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastapi_app():
    """测试 FastAPI 应用启动"""
    print("\n" + "=" * 60)
    print("测试 6: FastAPI 应用")
    print("=" * 60)
    
    try:
        from app.main import app
        print("✅ FastAPI 应用导入成功")
        
        # 检查路由
        routes = [r for r in app.routes if hasattr(r, 'path')]
        print(f"✅ 路由数量: {len(routes)}")
        
        # 检查关键路由
        paths = [r.path for r in routes]
        key_routes = ['/api/disciplines', '/api/majors', '/api/occupations']
        for route in key_routes:
            if route in paths:
                print(f"✅ 路由 {route} 存在")
            else:
                print(f"❌ 路由 {route} 缺失")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI 应用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("数据库连接测试脚本")
    print("=" * 60)
    
    results = []
    
    results.append(("基础模块导入", test_basic_imports()))
    results.append(("模型模块导入", test_models_import()))
    results.append(("数据库会话创建", test_database_session()))
    results.append(("CRUD 操作", test_crud_operations()))
    results.append(("数据库表结构", test_table_structure()))
    results.append(("FastAPI 应用", test_fastapi_app()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
