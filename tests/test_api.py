# -*- coding: utf-8 -*-
"""
测试用户画像模块API
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"
TEST_USER_ID = "test_user_001"

def test_create_profile():
    """测试创建用户画像"""
    print("\n[TEST] POST /user-profiles")
    try:
        response = requests.post(f"{BASE_URL}/user-profiles", json={
            "user_id": TEST_USER_ID,
            "nickname": "测试用户"
        }, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  OK: Profile created")
            return True
        elif response.status_code == 400:
            print(f"  Profile already exists, OK")
            return True
        else:
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"  Failed: {e}")
        return False

def test_get_profile():
    """测试获取用户画像"""
    print("\n[TEST] GET /user-profiles/{user_id}")
    try:
        response = requests.get(f"{BASE_URL}/user-profiles/{TEST_USER_ID}", timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  OK: Got profile for {data.get('nickname')}")
            return True
        else:
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"  Failed: {e}")
        return False

def test_chat():
    """测试RAG对话"""
    print("\n[TEST] POST /user-profiles/{user_id}/chat")
    try:
        response = requests.post(f"{BASE_URL}/user-profiles/{TEST_USER_ID}/chat", json={
            "message": "我对计算机专业感兴趣，喜欢编程",
            "context": {}
        }, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  OK: Got reply")
            print(f"  Reply: {data.get('reply', '')[:50]}...")
            print(f"  Extracted: {data.get('extracted_info', [])}")
            return True
        else:
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"  Failed: {e}")
        return False

def test_completeness():
    """测试完整度查询"""
    print("\n[TEST] GET /user-profiles/{user_id}/completeness")
    try:
        response = requests.get(f"{BASE_URL}/user-profiles/{TEST_USER_ID}/completeness", timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  OK: Completeness score = {data.get('score')}%")
            print(f"  Interface: {data.get('interface_layer_score')}%")
            print(f"  Variable: {data.get('variable_layer_score')}%")
            print(f"  Core: {data.get('core_layer_score')}%")
            return True
        else:
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"  Failed: {e}")
        return False

def test_visualization():
    """测试分层可视化"""
    print("\n[TEST] GET /user-profiles/{user_id}/visualization")
    try:
        response = requests.get(f"{BASE_URL}/user-profiles/{TEST_USER_ID}/visualization", timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  OK: Got layer visualization")
            print(f"  Layer status: {data.get('layer_status')}")
            return True
        else:
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"  Failed: {e}")
        return False

def main():
    print("=" * 60)
    print("User Profile Module API Test")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER_ID}")
    
    results = []
    
    # 测试各个接口
    results.append(("Create Profile", test_create_profile()))
    results.append(("Get Profile", test_get_profile()))
    results.append(("Chat", test_chat()))
    results.append(("Completeness", test_completeness()))
    results.append(("Visualization", test_visualization()))
    
    # 汇总
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\nTotal: {passed}/{total} passed")

if __name__ == "__main__":
    main()
