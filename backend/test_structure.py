#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试代码结构（不依赖DSPy安装）"""

import os
import sys

# 测试文件结构
print("=" * 60)
print("测试代码结构")
print("=" * 60)

test_files = [
    "app/rag_dspy/__init__.py",
    "app/rag_dspy/signatures/intent_signature.py",
    "app/rag_dspy/signatures/extract_signature.py",
    "app/rag_dspy/signatures/generate_signature.py",
    "app/rag_dspy/modules/intent_classifier.py",
    "app/rag_dspy/modules/info_extractor.py",
    "app/rag_dspy/modules/prompt_generator.py",
    "app/rag_dspy/modules/response_optimizer.py",
    "app/rag_dspy/dspy_rag_service.py",
]

print("\n文件结构检查:")
all_exist = True
for f in test_files:
    path = os.path.join(os.path.dirname(__file__), f)
    exists = os.path.exists(path)
    status = "OK" if exists else "MISSING"
    print(f"  [{status}] {f}")
    if not exists:
        all_exist = False

# 测试旧服务仍然可用
print("\n旧版RAG服务检查:")
try:
    from app.services.rag_service import get_rag_service
    service = get_rag_service()
    print(f"  [OK] Legacy RAG service loaded")
    print(f"       LLM available: {service.llm_available}")
except Exception as e:
    print(f"  [FAIL] {e}")

# 测试API路由
print("\nAPI路由检查:")
try:
    from app.api_user_profile import router, DSPY_AVAILABLE
    print(f"  [OK] API router loaded")
    print(f"       DSPY_AVAILABLE: {DSPY_AVAILABLE}")
except Exception as e:
    print(f"  [FAIL] {e}")

# 测试Schema
print("\nSchema检查:")
try:
    from app.schemas_user_profile import ChatMessageRequest, ChatMessageResponse
    
    # 测试preprocessed字段
    req = ChatMessageRequest(
        message="test",
        preprocessed={"intent": {"type": "test"}}
    )
    print(f"  [OK] Schema supports preprocessed field")
except Exception as e:
    print(f"  [FAIL] {e}")

print("\n" + "=" * 60)
if all_exist:
    print("结构检查通过！")
    print("\n下一步: 安装DSPy依赖")
    print("  pip install dspy-ai openai")
else:
    print("部分文件缺失，请检查")
