# -*- coding: utf-8 -*-
"""DSPy Signatures 定义"""

from .intent_signature import IntentClassification
from .extract_signature import StructuredInfoExtraction
from .generate_signature import DynamicPromptGeneration, ResponseOptimization

__all__ = [
    'IntentClassification',
    'StructuredInfoExtraction', 
    'DynamicPromptGeneration',
    'ResponseOptimization'
]
