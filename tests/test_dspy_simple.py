# -*- coding: utf-8 -*-
"""
简单验证DSPy模块加载
"""

import sys
sys.path.insert(0, 'backend')

print("1. Testing DSPy import...")
import dspy
print(f"   DSPy version: {dspy.__version__}")

print("\n2. Testing DSPy RAG service loading...")
import os
os.environ['LAZYLLM_KIMI_API_KEY'] = 'test-key-for-loading'

from app.rag_dspy import get_dspy_rag_service
service = get_dspy_rag_service()
print(f"   DSPy available: {service.dspy_available}")
print(f"   LLM configured: {service.llm is not None}")

print("\n3. Testing module imports...")
from app.rag_dspy.modules.intent_classifier import IntentClassifier, IntentMerger
from app.rag_dspy.modules.info_extractor import StructuredInfoExtractor, ContextAnalyzer
from app.rag_dspy.modules.prompt_generator import ContextualPromptGenerator
from app.rag_dspy.modules.response_optimizer import ResponseOptimizer, QuestionGenerator
print("   All modules imported successfully!")

print("\n4. Verifying module structure...")
print(f"   IntentClassifier: {IntentClassifier}")
print(f"   StructuredInfoExtractor: {StructuredInfoExtractor}")

print("\n[OK] DSPy module verification completed!")
print("\nNote: Actual function testing requires a valid API Key")
print("Please set LAZYLLM_KIMI_API_KEY or OPENAI_API_KEY environment variable")
