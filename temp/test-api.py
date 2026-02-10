#!/usr/bin/env python3
"""
API测试脚本 - 测试职业规划导航平台的后端API
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_api(endpoint, method="GET", data=None, description=""):
    """测试API接口"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🧪 测试: {description}")
    print(f"📡 {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"✅ 状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"📄 响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
            return True, result
        else:
            print(f"❌ 错误: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False, str(e)

def main():
    """主测试函数"""
    print("🚀 开始测试职业规划导航平台API...")
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    success_count = 0
    total_count = 0
    
    # 1. 测试根路径
    total_count += 1
    success, result = test_api("/", description="测试根路径")
    if success:
        success_count += 1
    
    # 2. 获取学科门类
    total_count += 1
    success, result = test_api("/disciplines", description="获取学科门类")
    if success:
        success_count += 1
        disciplines = result.get('data', {}).get('disciplines', [])
        if disciplines:
            discipline_id = disciplines[0]['id']
    
    # 3. 获取专业列表
    total_count += 1
    success, result = test_api("/majors", description="获取专业列表")
    if success:
        success_count += 1
        majors = result.get('data', [])
        if majors:
            major_id = majors[0]['id']
    
    # 4. 获取职业列表
    total_count += 1
    success, result = test_api("/occupations", description="获取职业列表")
    if success:
        success_count += 1
        occupations = result.get('data', {}).get('occupations', [])
        if occupations:
            occupation_id = occupations[0]['id']
    
    # 5. 搜索专业
    total_count += 1
    success, result = test_api("/majors/search?q=计算机", description="搜索专业")
    if success:
        success_count += 1
    
    # 6. 创建专业
    total_count += 1
    major_data = {
        "name": "人工智能",
        "code": "080907T",
        "category_id": 1,
        "description": "培养人工智能领域的专业人才",
        "duration": 4,
        "main_courses": ["机器学习", "深度学习", "自然语言处理"]
    }
    success, result = test_api("/majors", method="POST", data=major_data, description="创建专业")
    if success:
        success_count += 1
        created_major_id = result.get('data', {}).get('major', {}).get('id')
    
    # 7. 创建职业
    total_count += 1
    occupation_data = {
        "name": "AI工程师",
        "industry": "IT互联网",
        "description": "负责人工智能系统的设计和开发",
        "requirements": ["机器学习", "深度学习", "Python"],
        "salary_min": 15000,
        "salary_max": 60000
    }
    success, result = test_api("/occupations", method="POST", data=occupation_data, description="创建职业")
    if success:
        success_count += 1
        created_occupation_id = result.get('data', {}).get('occupation', {}).get('id')
    
    # 8. 创建个人经历
    total_count += 1
    experience_data = {
        "nickname": "测试用户",
        "major_id": 1,
        "education": "学士",
        "school_name": "测试大学",
        "degree": "计算机科学与技术学士",
        "experience": "毕业后从事软件开发工作，现在是一名高级软件工程师。",
        "is_anonymous": False
    }
    success, result = test_api("/experiences", method="POST", data=experience_data, description="创建个人经历")
    if success:
        success_count += 1
    
    # 9. 获取推荐职业
    if 'major_id' in locals():
        total_count += 1
        success, result = test_api(f"/recommendations/majors/{major_id}/occupations", description="获取推荐职业")
        if success:
            success_count += 1
    
    # 10. 初始化数据
    total_count += 1
    success, result = test_api("/init-data", method="POST", description="初始化数据库")
    if success:
        success_count += 1
    
    # 测试结果总结
    print(f"\n📊 测试结果总结:")
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")
    print(f"📈 成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！API服务运行正常。")
    else:
        print("\n⚠️  部分测试失败，请检查服务状态和日志。")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)