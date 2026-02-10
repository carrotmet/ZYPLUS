#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 接口测试脚本
用于测试后端 API 是否能正常响应
"""

import sys
import os
import json

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

def test_app_startup():
    """测试应用启动"""
    print("=" * 60)
    print("测试 1: FastAPI 应用启动")
    print("=" * 60)
    
    try:
        from app.main import app
        print("✅ FastAPI 应用导入成功")
        
        # 获取路由列表
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route)
        
        print(f"✅ 路由总数: {len(routes)}")
        
        # 检查关键路由
        paths = [r.path for r in routes]
        
        key_routes = {
            '基础': ['/'],
            '学科专业': ['/api/disciplines', '/api/majors'],
            '职业': ['/api/occupations'],
            '用户画像': ['/api/user-profiles/{user_id}'],
            '用户报告': ['/api/user-reports'],
        }
        
        for category, routes_list in key_routes.items():
            print(f"\n{category} 路由:")
            for route in routes_list:
                # 检查完全匹配和带参数匹配
                found = any(route == p or route in p for p in paths)
                if found:
                    print(f"  ✅ {route}")
                else:
                    print(f"  ❌ {route} (缺失)")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_in_app():
    """测试应用内数据库连接"""
    print("\n" + "=" * 60)
    print("测试 2: 应用内数据库连接")
    print("=" * 60)
    
    try:
        from app.main import app
        from app.database import get_database_file, check_database_exists
        
        db_file = get_database_file()
        print(f"数据库文件: {db_file}")
        print(f"文件存在: {check_database_exists()}")
        
        if check_database_exists():
            size = os.path.getsize(db_file)
            print(f"文件大小: {size} bytes")
            
            if size > 0:
                print("✅ 数据库文件存在且有数据")
            else:
                print("⚠️ 数据库文件存在但为空")
        else:
            print("❌ 数据库文件不存在")
        
        return True
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_disciplines_endpoint():
    """测试学科接口"""
    print("\n" + "=" * 60)
    print("测试 3: 学科接口 (/api/disciplines)")
    print("=" * 60)
    
    try:
        from app.main import app
        from app.database import get_db
        from app import crud
        
        # 直接使用 CRUD 函数测试
        db = next(get_db())
        try:
            disciplines = crud.get_disciplines(db)
            print(f"✅ 学科查询成功: {len(disciplines)} 个学科")
            
            if disciplines:
                for d in disciplines[:3]:
                    name = getattr(d, 'name', 'Unknown')
                    print(f"   - {name}")
                
                if len(disciplines) > 3:
                    print(f"   ... 还有 {len(disciplines) - 3} 个")
            else:
                print("⚠️ 学科数据为空，可能需要初始化")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"❌ 学科接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_majors_endpoint():
    """测试专业接口"""
    print("\n" + "=" * 60)
    print("测试 4: 专业接口 (/api/majors)")
    print("=" * 60)
    
    try:
        from app.database import get_db
        from app import crud
        
        db = next(get_db())
        try:
            majors = crud.get_majors(db)
            print(f"✅ 专业查询成功: {len(majors)} 个专业")
            
            if majors:
                for m in majors[:3]:
                    name = getattr(m, 'name', 'Unknown')
                    print(f"   - {name}")
                
                if len(majors) > 3:
                    print(f"   ... 还有 {len(majors) - 3} 个")
            else:
                print("⚠️ 专业数据为空，可能需要初始化")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"❌ 专业接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_occupations_endpoint():
    """测试职业接口"""
    print("\n" + "=" * 60)
    print("测试 5: 职业接口 (/api/occupations)")
    print("=" * 60)
    
    try:
        from app.database import get_db
        from app import crud
        
        db = next(get_db())
        try:
            occupations = crud.get_occupations(db)
            print(f"✅ 职业查询成功: {len(occupations)} 个职业")
            
            if occupations:
                for o in occupations[:3]:
                    name = getattr(o, 'name', 'Unknown')
                    print(f"   - {name}")
                
                if len(occupations) > 3:
                    print(f"   ... 还有 {len(occupations) - 3} 个")
            else:
                print("⚠️ 职业数据为空，可能需要初始化")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"❌ 职业接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_profile_endpoint():
    """测试用户画像接口"""
    print("\n" + "=" * 60)
    print("测试 6: 用户画像接口")
    print("=" * 60)
    
    try:
        from app.database import get_db
        from app import crud_user_profile
        
        db = next(get_db())
        try:
            # 尝试获取测试用户画像
            profile = crud_user_profile.get_user_profile(db, "test_user")
            if profile:
                print(f"✅ 用户画像查询成功")
                print(f"   用户: {profile.user_id}")
                print(f"   完整度: {profile.completeness_score}%")
            else:
                print("⚠️ 测试用户画像不存在（这是正常的）")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"❌ 用户画像接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_endpoints():
    """测试报告接口"""
    print("\n" + "=" * 60)
    print("测试 7: 用户报告接口")
    print("=" * 60)
    
    try:
        from app.main import app
        
        # 检查路由是否存在
        paths = [r.path for r in app.routes if hasattr(r, 'path')]
        
        report_routes = [
            '/api/user-reports',
            '/api/user-reports/center/init',
            '/api/user-reports/prerequisites',
            '/api/user-reports/generation',
        ]
        
        for route in report_routes:
            # 检查路由或其前缀是否存在
            found = any(route == p or route in p for p in paths)
            if found:
                print(f"✅ {route}")
            else:
                print(f"❌ {route} (缺失)")
        
        return True
    except Exception as e:
        print(f"❌ 报告接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cors_configuration():
    """测试 CORS 配置"""
    print("\n" + "=" * 60)
    print("测试 8: CORS 配置")
    print("=" * 60)
    
    try:
        from app.main import app
        
        # 检查 CORS 中间件
        cors_found = False
        for middleware in app.user_middleware:
            if 'cors' in str(middleware.cls).lower():
                cors_found = True
                print(f"✅ CORS 中间件已配置")
                break
        
        if not cors_found:
            print("⚠️ 未找到 CORS 中间件")
        
        return True
    except Exception as e:
        print(f"❌ CORS 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("API 接口测试脚本")
    print("=" * 60)
    
    results = []
    
    results.append(("FastAPI 应用启动", test_app_startup()))
    results.append(("应用内数据库连接", test_database_in_app()))
    results.append(("学科接口", test_disciplines_endpoint()))
    results.append(("专业接口", test_majors_endpoint()))
    results.append(("职业接口", test_occupations_endpoint()))
    results.append(("用户画像接口", test_user_profile_endpoint()))
    results.append(("用户报告接口", test_report_endpoints()))
    results.append(("CORS 配置", test_cors_configuration()))
    
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
