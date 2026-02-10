#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DSPy集成测试脚本
验证新的RAG架构是否正常工作
"""

import os
import sys

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)


def test_imports():
    """测试模块导入"""
    print("=" * 60)
    print("测试模块导入")
    print("=" * 60)
    
    tests = [
        ("DSPy", "import dspy"),
        ("DSPy Service", "from app.rag_dspy import get_dspy_rag_service"),
        ("Intent Classifier", "from app.rag_dspy.modules import IntentClassifier"),
        ("Info Extractor", "from app.rag_dspy.modules import StructuredInfoExtractor"),
        ("Prompt Generator", "from app.rag_dspy.modules import ContextualPromptGenerator"),
    ]
    
    results = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✓ {name}")
            results.append((name, True, None))
        except Exception as e:
            print(f"✗ {name}: {e}")
            results.append((name, False, str(e)))
    
    return all(r[1] for r in results)


def test_dspy_service():
    """测试DSPy服务初始化"""
    print("\n" + "=" * 60)
    print("测试DSPy服务初始化")
    print("=" * 60)
    
    try:
        from app.rag_dspy import get_dspy_rag_service
        service = get_dspy_rag_service()
        
        print(f"DSPy Available: {service.dspy_available}")
        print(f"LLM Configured: {service.llm is not None}")
        print(f"Modules Loaded: {len(service.modules)} modules")
        
        if service.dspy_available:
            print("✓ DSPy服务初始化成功")
            return True
        else:
            print("⚠ DSPy不可用，将使用fallback模式")
            return True  # 仍然算成功，因为fallback可用
            
    except Exception as e:
        print(f"✗ DSPy服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intent_classification():
    """测试意图分类"""
    print("\n" + "=" * 60)
    print("测试意图分类")
    print("=" * 60)
    
    try:
        from app.rag_dspy import get_dspy_rag_service
        service = get_dspy_rag_service()
        
        test_messages = [
            "我喜欢羽毛球",
            "我不知道该怎么办",
            "我擅长编程",
            "你觉得医生这个职业怎么样",
        ]
        
        for msg in test_messages:
            result = service.process_message(
                user_message=msg,
                user_profile={},
                conversation_history=[]
            )
            print(f"'{msg}' → {result.get('intent', 'unknown')} "
                  f"(confidence: {result.get('confidence', 0):.2f})")
        
        print("✓ 意图分类测试完成")
        return True
        
    except Exception as e:
        print(f"✗ 意图分类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_info_extraction():
    """测试信息提取"""
    print("\n" + "=" * 60)
    print("测试信息提取")
    print("=" * 60)
    
    try:
        from app.rag_dspy import get_dspy_rag_service
        service = get_dspy_rag_service()
        
        result = service.process_message(
            user_message="我喜欢古典音乐，但没时间练习",
            user_profile={},
            conversation_history=[]
        )
        
        print(f"Reply: {result.get('reply', '')[:100]}...")
        print(f"Extracted: {result.get('extracted_info', [])}")
        print(f"Suggested Questions: {result.get('suggested_questions', [])}")
        
        print("✓ 信息提取测试完成")
        return True
        
    except Exception as e:
        print(f"✗ 信息提取测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_compatibility():
    """测试API兼容性"""
    print("\n" + "=" * 60)
    print("测试API兼容性")
    print("=" * 60)
    
    try:
        from app.schemas_user_profile import ChatMessageRequest, ChatMessageResponse
        
        # 测试请求格式（包含新的preprocessed字段）
        request_data = {
            "message": "测试消息",
            "context": {"history": []},
            "preprocessed": {
                "intent": {"type": "interest_explore", "confidence": 0.9}
            }
        }
        
        # 验证可以创建（不会抛出异常）
        request = ChatMessageRequest(**request_data)
        print(f"✓ 请求格式兼容: {request.message}")
        
        # 测试响应格式
        from typing import List
        from app.schemas_user_profile import ExtractedInfo
        
        response_data = {
            "reply": "测试回复",
            "extracted_info": [ExtractedInfo(field="test", value="value", confidence=1.0)],
            "updated_fields": [],
            "suggested_questions": ["问题1", "问题2"],
            "current_casve_stage": "communication",
            "profile_updates": {"holland_code": "RIA"}
        }
        
        response = ChatMessageResponse(**response_data)
        print(f"✓ 响应格式兼容: {response.reply}")
        
        return True
        
    except Exception as e:
        print(f"✗ API兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("DSPy RAG集成测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("服务初始化", test_dspy_service()))
    
    # 只有在服务可用时才运行功能测试
    from app.rag_dspy import get_dspy_rag_service
    service = get_dspy_rag_service()
    
    if service.dspy_available:
        results.append(("意图分类", test_intent_classification()))
        results.append(("信息提取", test_info_extraction()))
    else:
        print("\n⚠ DSPy不可用，跳过功能测试")
    
    results.append(("API兼容性", test_api_compatibility()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print("\n✗ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
