# -*- coding: utf-8 -*-
"""
用户报告模块 - 生成条件检查器
基于 Career-Planning SKILL 三层模型设计
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from .schemas_user_report import ReportType, PrerequisiteItem
from .models_user_profile import UserProfile
from .models_user_report import GenerationTask


class ConditionStatus(str, Enum):
    """条件状态"""
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class ConditionCheck:
    """条件检查结果"""
    id: str
    name: str
    description: str
    status: ConditionStatus
    current_value: Any = None
    required_value: str = ""
    weight: int = 10
    recommendation: Optional[str] = None
    check_func: Callable = field(default=None, repr=False)


class ReportPrerequisitesChecker:
    """
    报告生成条件检查器
    
    设计原则:
    1. 子报告A(用户画像): 接口层完整度 ≥ 60%
    2. 子报告B(表单分析): 表单填写次数 ≥ 3
    3. 子报告C(三层建模): 可变层完整度 ≥ 50%
    4. 子报告D(行动体系): 核心层universal_skills有值
    5. 完整报告: 以上所有 + 总完整度 ≥ 70%
    """
    
    # 条件定义
    CONDITIONS = {
        # 子报告A: 用户画像深度分析报告
        "A1": {
            "id": "A1",
            "name": "接口层基础信息",
            "description": "需要完成Holland职业兴趣测评和MBTI性格测试",
            "weight": 10,
            "check": lambda p: p.holland_code is not None and p.mbti_type is not None,
            "get_value": lambda p: f"{p.holland_code}, {p.mbti_type}" if p.holland_code and p.mbti_type else None,
            "required": "Holland代码和MBTI类型",
            "recommendation": "请先完成Holland职业兴趣测评和MBTI性格测试"
        },
        "A2": {
            "id": "A2",
            "name": "接口层完整度",
            "description": "接口层完整度需要达到60%以上",
            "weight": 10,
            "check": lambda p: _calculate_interface_completeness(p) >= 60,
            "get_value": lambda p: _calculate_interface_completeness(p),
            "required": ">= 60%",
            "recommendation": "请完善价值观优先级或能力评估信息"
        },
        
        # 子报告B: 用户表单分析报告
        "B1": {
            "id": "B1",
            "name": "表单填写次数",
            "description": "需要至少完成3次表单更新",
            "weight": 10,
            "check": lambda p, logs=0: logs >= 3,  # logs需要外部传入
            "get_value": lambda p, logs=0: logs,
            "required": ">= 3次",
            "recommendation": "请前往用户画像页面完善更多信息"
        },
        "B2": {
            "id": "B2",
            "name": "CASVE决策阶段",
            "description": "需要确定当前CASVE决策阶段",
            "weight": 10,
            "check": lambda p: p.current_casve_stage is not None and p.current_casve_stage != 'communication',
            "get_value": lambda p: p.current_casve_stage,
            "required": "非初始阶段",
            "recommendation": "请先确定您当前的职业决策阶段"
        },
        
        # 子报告C: 三层职业规划建模报告
        "C1": {
            "id": "C1",
            "name": "可变层路径偏好",
            "description": "需要设置职业路径偏好",
            "weight": 10,
            "check": lambda p: p.career_path_preference is not None,
            "get_value": lambda p: p.career_path_preference,
            "required": "非空",
            "recommendation": "请设置您的职业路径偏好(技术/管理/专业/公职)"
        },
        "C2": {
            "id": "C2",
            "name": "可变层专业偏好",
            "description": "需要至少选择一个感兴趣的专业",
            "weight": 10,
            "check": lambda p: p.preferred_majors is not None and len(p.preferred_majors) > 0,
            "get_value": lambda p: len(p.preferred_majors) if p.preferred_majors else 0,
            "required": ">= 1个专业",
            "recommendation": "请至少选择一个您感兴趣的专业"
        },
        "C3": {
            "id": "C3",
            "name": "可变层完整度",
            "description": "可变层完整度需要达到50%以上",
            "weight": 10,
            "check": lambda p: _calculate_variable_completeness(p) >= 50,
            "get_value": lambda p: _calculate_variable_completeness(p),
            "required": ">= 50%",
            "recommendation": "请完善专业偏好或实践经历信息"
        },
        
        # 子报告D: 分层递进行动体系报告
        "D1": {
            "id": "D1",
            "name": "核心层通用技能",
            "description": "需要进行通用技能评估",
            "weight": 10,
            "check": lambda p: p.universal_skills is not None and len(p.universal_skills) > 0,
            "get_value": lambda p: list(p.universal_skills.keys()) if p.universal_skills else [],
            "required": "非空",
            "recommendation": "请先进行通用技能评估"
        },
        "D2": {
            "id": "D2",
            "name": "核心层CASVE历史",
            "description": "需要至少完成一轮CASVE决策循环记录",
            "weight": 10,
            "check": lambda p: p.casve_history is not None and len(p.casve_history) > 0,
            "get_value": lambda p: len(p.casve_history) if p.casve_history else 0,
            "required": ">= 1条记录",
            "recommendation": "请记录您的CASVE决策过程"
        },
        
        # 完整报告条件
        "F1": {
            "id": "F1",
            "name": "总完整度",
            "description": "整体画像完整度需要达到70%以上",
            "weight": 20,
            "check": lambda p: (p.completeness_score or 0) >= 70,
            "get_value": lambda p: p.completeness_score or 0,
            "required": ">= 70%",
            "recommendation": "请完善更多维度的画像信息"
        },
        "F2": {
            "id": "F2",
            "name": "所有子报告条件",
            "description": "需要满足所有子报告的生成条件",
            "weight": 20,
            "check": lambda checks: all(
                checks.get(f"A{i}", {}).get("status") == ConditionStatus.PASSED 
                for i in [1, 2]
            ) and checks.get("B1", {}).get("status") == ConditionStatus.PASSED,
            "get_value": lambda checks: sum(1 for c in checks.values() if c.get("status") == ConditionStatus.PASSED),
            "required": "A1,A2,B1通过",
            "recommendation": "请先完成各子报告的生成条件"
        }
    }
    
    # 报告类型所需条件
    REPORT_PREREQUISITES = {
        ReportType.SUB_REPORT_A: ["A1", "A2"],
        ReportType.SUB_REPORT_B: ["B1", "B2"],
        ReportType.SUB_REPORT_C: ["C1", "C2", "C3"],
        ReportType.SUB_REPORT_D: ["D1", "D2"],
        ReportType.FULL_REPORT: ["F1", "F2", "A1", "A2", "B1", "C1", "D1"]
    }
    
    def __init__(self, profile: UserProfile, form_submission_count: int = 0):
        """
        初始化检查器
        
        Args:
            profile: 用户画像对象
            form_submission_count: 表单提交次数
        """
        self.profile = profile
        self.form_submission_count = form_submission_count
        self._check_results: Dict[str, Dict] = {}
    
    def check_all(self, report_type: ReportType) -> Dict[str, Any]:
        """
        检查指定报告类型的所有条件
        
        Returns:
            {
                "can_generate": bool,
                "overall_progress": int,
                "prerequisites": List[PrerequisiteItem],
                "next_steps": List[str]
            }
        """
        condition_ids = self.REPORT_PREREQUISITES.get(report_type, [])
        prerequisites = []
        passed_count = 0
        total_weight = 0
        passed_weight = 0
        next_steps = []
        
        for condition_id in condition_ids:
            condition_def = self.CONDITIONS.get(condition_id)
            if not condition_def:
                continue
            
            # 执行检查
            passed, current_value = self._execute_check(condition_id, condition_def)
            
            total_weight += condition_def["weight"]
            if passed:
                passed_count += 1
                passed_weight += condition_def["weight"]
            else:
                next_steps.append(condition_def["recommendation"])
            
            # 保存检查结果
            self._check_results[condition_id] = {
                "status": ConditionStatus.PASSED if passed else ConditionStatus.FAILED,
                "value": current_value
            }
            
            # 构建PrerequisiteItem
            prereq = PrerequisiteItem(
                id=condition_def["id"],
                name=condition_def["name"],
                description=condition_def["description"],
                status=ConditionStatus.PASSED if passed else ConditionStatus.FAILED,
                current_value=current_value,
                required_value=condition_def["required"],
                weight=condition_def["weight"],
                recommendation=condition_def["recommendation"] if not passed else None
            )
            prerequisites.append(prereq)
        
        # 计算整体进度 (加权)
        overall_progress = int((passed_weight / total_weight * 100) if total_weight > 0 else 0)
        can_generate = passed_count == len(condition_ids)
        
        return {
            "report_type": report_type,
            "can_generate": can_generate,
            "overall_progress": overall_progress,
            "prerequisites": prerequisites,
            "next_steps": list(set(next_steps))  # 去重
        }
    
    def check_single(self, condition_id: str) -> Optional[Dict]:
        """检查单个条件"""
        condition_def = self.CONDITIONS.get(condition_id)
        if not condition_def:
            return None
        
        passed, current_value = self._execute_check(condition_id, condition_def)
        
        return {
            "id": condition_id,
            "passed": passed,
            "current_value": current_value,
            "required": condition_def["required"],
            "recommendation": condition_def["recommendation"] if not passed else None
        }
    
    def _execute_check(self, condition_id: str, condition_def: Dict) -> tuple[bool, Any]:
        """执行条件检查"""
        check_func = condition_def["check"]
        get_value_func = condition_def["get_value"]
        
        try:
            # 特殊处理需要check_results的条件
            if condition_id == "F2":
                passed = check_func(self._check_results)
            # 特殊处理需要form_submission_count的条件
            elif condition_id == "B1":
                passed = check_func(self.profile, self.form_submission_count)
            else:
                passed = check_func(self.profile)
            
            # 获取当前值
            if condition_id == "F2":
                current_value = get_value_func(self._check_results)
            elif condition_id == "B1":
                current_value = get_value_func(self.profile, self.form_submission_count)
            else:
                current_value = get_value_func(self.profile)
            
            return bool(passed), current_value
        except Exception as e:
            # 检查失败，返回False
            return False, None
    
    def get_estimated_time(self, report_type: ReportType) -> int:
        """获取预估生成时间(秒)"""
        time_estimates = {
            ReportType.SUB_REPORT_A: 90,    # 1.5分钟
            ReportType.SUB_REPORT_B: 72,    # 1.2分钟
            ReportType.SUB_REPORT_C: 120,   # 2分钟
            ReportType.SUB_REPORT_D: 108,   # 1.8分钟
            ReportType.FULL_REPORT: 300     # 5分钟
        }
        return time_estimates.get(report_type, 300)
    
    def get_estimated_words(self, report_type: ReportType) -> int:
        """获取预估字数"""
        word_estimates = {
            ReportType.SUB_REPORT_A: 8000,
            ReportType.SUB_REPORT_B: 6000,
            ReportType.SUB_REPORT_C: 15000,
            ReportType.SUB_REPORT_D: 12000,
            ReportType.FULL_REPORT: 50000
        }
        return word_estimates.get(report_type, 50000)


# ==================== 辅助函数 ====================

def _calculate_interface_completeness(profile: UserProfile) -> int:
    """计算接口层完整度"""
    fields = [
        profile.holland_code is not None,
        profile.mbti_type is not None,
        profile.value_priorities is not None and len(profile.value_priorities) > 0,
        profile.ability_assessment is not None and len(profile.ability_assessment) > 0,
        profile.constraints is not None
    ]
    return int(sum(fields) / len(fields) * 100)


def _calculate_variable_completeness(profile: UserProfile) -> int:
    """计算可变层完整度"""
    fields = [
        profile.preferred_disciplines is not None and len(profile.preferred_disciplines) > 0,
        profile.preferred_majors is not None and len(profile.preferred_majors) > 0,
        profile.career_path_preference is not None,
        profile.practice_experiences is not None and len(profile.practice_experiences) > 0
    ]
    return int(sum(fields) / len(fields) * 100)


def _calculate_core_completeness(profile: UserProfile) -> int:
    """计算核心层完整度"""
    fields = [
        profile.current_casve_stage is not None,
        profile.casve_history is not None and len(profile.casve_history) > 0,
        profile.universal_skills is not None and len(profile.universal_skills) > 0,
        profile.resilience_score is not None
    ]
    return int(sum(fields) / len(fields) * 100)


# ==================== 便捷函数 ====================

def check_report_prerequisites(
    profile: UserProfile,
    report_type: ReportType,
    form_submission_count: int = 0
) -> Dict[str, Any]:
    """
    便捷函数: 检查报告生成条件
    
    Args:
        profile: 用户画像
        report_type: 报告类型
        form_submission_count: 表单提交次数
    
    Returns:
        条件检查结果
    """
    checker = ReportPrerequisitesChecker(profile, form_submission_count)
    return checker.check_all(report_type)


def can_generate_report(
    profile: UserProfile,
    report_type: ReportType,
    form_submission_count: int = 0
) -> bool:
    """
    便捷函数: 判断是否可以生成报告
    
    Args:
        profile: 用户画像
        report_type: 报告类型
        form_submission_count: 表单提交次数
    
    Returns:
        是否可以生成
    """
    result = check_report_prerequisites(profile, report_type, form_submission_count)
    return result["can_generate"]
