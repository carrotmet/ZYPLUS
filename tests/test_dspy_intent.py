# -*- coding: utf-8 -*-
"""
测试DSPy意图识别与信息抽取模块
"""

import sys
import os

# 添加backend到路径
sys.path.insert(0, 'backend')

# 设置测试API Key（如果没有设置）
if not os.environ.get('LAZYLLM_KIMI_API_KEY') and not os.environ.get('OPENAI_API_KEY'):
    print("[Warning] 未设置API Key，将使用mock模式测试")
    print("请设置环境变量: LAZYLLM_KIMI_API_KEY 或 OPENAI_API_KEY")
    print()

from app.rag_dspy import get_dspy_rag_service

def test_intent_classification():
    """测试意图分类功能"""
    print("=" * 60)
    print("测试1: 意图分类")
    print("=" * 60)
    
    service = get_dspy_rag_service()
    
    if not service.dspy_available:
        print("[Error] DSPy服务不可用，跳过测试")
        return False
    
    test_messages = [
        "我喜欢编程和解决技术问题",
        "我擅长数学和逻辑分析",
        "对我来说，工作的稳定性和成就感很重要",
        "软件工程师这个职业前景怎么样？",
        "我不知道该选计算机还是金融专业",
        "最近很焦虑，不知道未来该做什么",
    ]
    
    expected_intents = [
        "interest_explore",
        "ability_assess",
        "value_clarify",
        "career_advice",
        "casve_guidance",
        "emotional_support"
    ]
    
    from app.rag_dspy.modules.intent_classifier import IntentClassifier
    
    classifier = IntentClassifier()
    
    for msg, expected in zip(test_messages, expected_intents):
        result = classifier(
            user_message=msg,
            conversation_history=[],
            current_profile={}
        )
        print(f"\n用户: {msg}")
        print(f"识别意图: {result['intent_type']}")
        print(f"置信度: {result['confidence']:.2f}")
        print(f"推理: {result['reasoning'][:80]}...")
        print(f"期望意图: {expected}")
        print(f"情感状态: {result.get('emotional_state', 'neutral')}")
        print("-" * 40)
    
    return True

def test_info_extraction():
    """测试信息抽取功能"""
    print("\n" + "=" * 60)
    print("测试2: 结构化信息抽取")
    print("=" * 60)
    
    service = get_dspy_rag_service()
    
    if not service.dspy_available:
        print("[Error] DSPy服务不可用，跳过测试")
        return False
    
    from app.rag_dspy.modules.info_extractor import StructuredInfoExtractor
    
    extractor = StructuredInfoExtractor()
    
    test_cases = [
        {
            "message": "我喜欢弹钢琴和绘画，但没时间练习",
            "intent": "interest_explore"
        },
        {
            "message": "我擅长Python编程和数据分析，做过几个项目",
            "intent": "ability_assess"
        },
        {
            "message": "我追求创新和自由的工作环境",
            "intent": "value_clarify"
        }
    ]
    
    for case in test_cases:
        result = extractor(
            user_message=case["message"],
            intent_type=case["intent"],
            profile_context={},
            conversation_context=[]
        )
        print(f"\n用户: {case['message']}")
        print(f"意图: {case['intent']}")
        print(f"提取的兴趣: {result.get('interests', [])}")
        print(f"提取的能力: {result.get('abilities', [])}")
        print(f"提取的价值观: {result.get('values', [])}")
        print(f"提取的约束: {result.get('constraints', [])}")
        print(f"画像更新建议: {result.get('profile_updates', {})}")
        print("-" * 40)
    
    return True

def test_full_pipeline():
    """测试完整流程"""
    print("\n" + "=" * 60)
    print("测试3: 完整对话流程")
    print("=" * 60)
    
    service = get_dspy_rag_service()
    
    if not service.dspy_available:
        print("[Error] DSPy服务不可用，跳过测试")
        return False
    
    # 模拟对话历史
    conversation_history = []
    
    # 模拟用户画像
    user_profile = {
        "holland_code": None,
        "mbti_type": None,
        "value_priorities": [],
        "ability_assessment": {},
        "career_path_preference": None,
        "current_casve_stage": "communication",
        "completeness_score": 10
    }
    
    test_messages = [
        "你好，我想了解一下适合我的职业方向",
        "我喜欢编程，特别是后端开发",
        "我擅长逻辑分析和问题解决",
        "我希望工作有挑战性，不想太枯燥",
    ]
    
    for msg in test_messages:
        print(f"\n用户: {msg}")
        
        # 模拟前端预处理
        preprocessed = {
            "intent": {
                "type": "interest_explore" if "喜欢" in msg else "general_chat",
                "confidence": 0.8
            },
            "entities": {
                "interests": ["编程"] if "编程" in msg else [],
                "abilities": ["逻辑分析"] if "逻辑" in msg else []
            }
        }
        
        result = service.process_message(
            user_message=msg,
            user_profile=user_profile,
            conversation_history=conversation_history,
            preprocessed=preprocessed
        )
        
        print(f"AI: {result['reply'][:100]}...")
        print(f"识别意图: {result['intent']}")
        print(f"提取信息: {result['extracted_info']}")
        print(f"建议问题: {result.get('suggested_questions', [])}")
        print(f"对话阶段: {result['conversation_stage']}")
        print("-" * 40)
        
        # 更新对话历史
        conversation_history.append({"role": "user", "content": msg})
        conversation_history.append({"role": "assistant", "content": result['reply']})
    
    return True

def test_context_analyzer():
    """测试上下文分析器"""
    print("\n" + "=" * 60)
    print("测试4: 上下文分析")
    print("=" * 60)
    
    service = get_dspy_rag_service()
    
    if not service.dspy_available:
        print("[Error] DSPy服务不可用，跳过测试")
        return False
    
    from app.rag_dspy.modules.info_extractor import ContextAnalyzer
    
    analyzer = ContextAnalyzer()
    
    # 模拟有上下文的对话
    previous_messages = [
        {"role": "user", "content": "我对计算机专业感兴趣"},
        {"role": "assistant", "content": "计算机专业是一个很好的选择，你有编程基础吗？"},
    ]
    
    current_message = "我学过一点Python"
    
    result = analyzer(
        current_message=current_message,
        previous_messages=previous_messages
    )
    
    print(f"当前消息: {current_message}")
    print(f"话题转换: {result.get('topic_transition')}")
    print(f"隐含需求: {result.get('implicit_needs')}")
    print(f"建议语气: {result.get('suggested_tone')}")
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DSPy意图识别与信息抽取模块测试")
    print("=" * 60)
    
    # 运行所有测试
    results = []
    
    try:
        results.append(("意图分类", test_intent_classification()))
    except Exception as e:
        print(f"[Error] 意图分类测试失败: {e}")
        results.append(("意图分类", False))
    
    try:
        results.append(("信息抽取", test_info_extraction()))
    except Exception as e:
        print(f"[Error] 信息抽取测试失败: {e}")
        results.append(("信息抽取", False))
    
    try:
        results.append(("上下文分析", test_context_analyzer()))
    except Exception as e:
        print(f"[Error] 上下文分析测试失败: {e}")
        results.append(("上下文分析", False))
    
    try:
        results.append(("完整流程", test_full_pipeline()))
    except Exception as e:
        print(f"[Error] 完整流程测试失败: {e}")
        results.append(("完整流程", False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
