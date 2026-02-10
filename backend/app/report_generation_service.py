# -*- coding: utf-8 -*-
"""
用户报告模块 - 报告生成服务
基于LazyLLM的并行报告生成工作流
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.orm import Session

# LazyLLM导入
# from lazyllm import pipeline, parallel, switch, OnlineChatModule
# from lazyllm.components import ChatPrompter

from .models_user_report import (
    UserReport, ReportChapter, GenerationTask, ReportSnapshot, GenerationLog
)
from .schemas_user_report import (
    ReportType, TaskStatus, ChapterStatus, GenerationOptions,
    WebSocketMessage, GenerationProgressUpdate
)
from .crud_user_report import (
    create_user_report, update_user_report, create_report_chapter,
    update_chapter_content, update_generation_task, create_generation_log,
    increment_task_retry, create_report_snapshot
)
from .report_prerequisites import ReportPrerequisitesChecker


# ==================== 章节配置定义 ====================

@dataclass
class ChapterConfig:
    """章节配置"""
    code: str
    title: str
    word_count: int
    parent_code: Optional[str] = None
    level: int = 1
    report_types: List[ReportType] = None
    prompt_template: str = ""
    
    def __post_init__(self):
        if self.report_types is None:
            self.report_types = []


# 章节配置表
CHAPTER_CONFIGS: Dict[str, ChapterConfig] = {
    # 第一章: 执行摘要 (仅完整报告)
    "1": ChapterConfig(
        code="1",
        title="第一章: 执行摘要",
        word_count=2000,
        level=1,
        report_types=[ReportType.FULL_REPORT],
        prompt_template="""
基于以下用户画像数据，撰写职业规划报告的执行摘要(约2000字)：

用户画像：
- Holland代码: {holland_code}
- MBTI类型: {mbti_type}
- 价值观: {value_priorities}
- 能力评估: {ability_assessment}
- 职业路径偏好: {career_path_preference}
- CASVE阶段: {current_casve_stage}

要求：
1. 概述用户的核心特征和职业倾向
2. 总结关键发现和建议
3. 提供报告阅读指南
4. 字数控制在2000字左右
"""
    ),
    
    # 第二章: 用户画像深度分析 (子报告A + 完整报告)
    "2": ChapterConfig(
        code="2",
        title="第二章: 用户画像深度分析",
        word_count=8000,
        level=1,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT]
    ),
    "2.1": ChapterConfig(
        code="2.1",
        title="2.1 接口层画像解析",
        word_count=6000,
        parent_code="2",
        level=2,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT]
    ),
    "2.1.1": ChapterConfig(
        code="2.1.1",
        title="2.1.1 Holland职业兴趣分析",
        word_count=2000,
        parent_code="2.1",
        level=3,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT],
        prompt_template="""
为用户撰写Holland职业兴趣分析章节(约2000字)。

用户Holland代码: {holland_code}

请从以下维度展开：
1. 代码解读：详细解释该Holland代码的含义和特征
2. 类型特征：描述该类型的典型行为模式和工作偏好
3. 适配职业：推荐适合的职业领域和具体职业
4. 发展建议：针对该类型给出职业发展建议
5. 注意事项：该类型可能面临的挑战和应对策略

要求：
- 内容专业、深入、有洞察力
- 结合用户的具体情况进行分析
- 字数控制在2000字左右
"""
    ),
    "2.1.2": ChapterConfig(
        code="2.1.2",
        title="2.1.2 MBTI性格类型分析",
        word_count=2000,
        parent_code="2.1",
        level=3,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT],
        prompt_template="""
为用户撰写MBTI性格类型分析章节(约2000字)。

用户MBTI类型: {mbti_type}

请从以下维度展开：
1. 类型解析：详细解释该MBTI类型的四个维度特征
2. 认知功能：描述主导功能和辅助功能
3. 职业匹配：分析该类型适合的职业环境和工作方式
4. 团队协作：该类型在团队中的角色和协作建议
5. 成长方向：个人发展和完善建议

要求：
- 结合职业规划场景进行分析
- 提供具体可行的建议
- 字数控制在2000字左右
"""
    ),
    "2.1.3": ChapterConfig(
        code="2.1.3",
        title="2.1.3 价值观优先级分析",
        word_count=1500,
        parent_code="2.1",
        level=3,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT],
        prompt_template="""
为用户撰写价值观优先级分析章节(约1500字)。

用户价值观排序: {value_priorities}

请从以下维度展开：
1. 价值观解读：分析各价值观的含义和重要性
2. 优先级分析：解读排序背后的深层需求
3. 职业影响：这些价值观如何影响职业选择
4. 匹配建议：推荐符合这些价值观的职业类型
5. 平衡策略：如何处理价值观之间的冲突

要求：
- 深入分析用户的价值取向
- 联系实际职业场景
- 字数控制在1500字左右
"""
    ),
    "2.1.4": ChapterConfig(
        code="2.1.4",
        title="2.1.4 能力评估矩阵",
        word_count=1500,
        parent_code="2.1",
        level=3,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT],
        prompt_template="""
为用户撰写能力评估矩阵分析章节(约1500字)。

用户能力评估: {ability_assessment}

请从以下维度展开：
1. 能力画像：分析用户在各项能力上的表现
2. 优势能力：识别和强化核心优势
3. 发展能力：指出需要提升的能力领域
4. 职业匹配：基于能力特点推荐适合的职业
5. 提升路径：针对性的能力提升建议

要求：
- 客观分析能力现状
- 提供具体的发展路径
- 字数控制在1500字左右
"""
    ),
    "2.2": ChapterConfig(
        code="2.2",
        title="2.2 可变层画像解析",
        word_count=1000,
        parent_code="2",
        level=2,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT]
    ),
    "2.2.1": ChapterConfig(
        code="2.2.1",
        title="2.2.1 偏好学科分析",
        word_count=500,
        parent_code="2.2",
        level=3,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT],
        prompt_template="""
分析用户的偏好学科(约500字)：

偏好学科: {preferred_disciplines}
偏好专业: {preferred_majors}

请分析：
1. 学科偏好特征
2. 专业匹配度
3. 发展方向建议
"""
    ),
    "2.2.2": ChapterConfig(
        code="2.2.2",
        title="2.2.2 职业路径倾向",
        word_count=500,
        parent_code="2.2",
        level=3,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT],
        prompt_template="""
分析用户的职业路径倾向(约500字)：

职业路径偏好: {career_path_preference}

请分析：
1. 路径特征解读
2. 发展优势分析
3. 关键成功因素
"""
    ),
    "2.3": ChapterConfig(
        code="2.3",
        title="2.3 三层画像综合解读",
        word_count=1000,
        parent_code="2",
        level=2,
        report_types=[ReportType.SUB_REPORT_A, ReportType.FULL_REPORT],
        prompt_template="""
基于三层模型综合解读用户画像(约1000字)。

接口层: {interface_summary}
可变层: {variable_summary}
核心层: {core_summary}

请从以下维度展开：
1. 三层整合分析
2. 一致性检验
3. 矛盾点识别与调和
4. 综合画像结论

要求：
- 整合三个层次的特征
- 形成完整的用户画像
- 字数控制在1000字左右
"""
    ),
    
    # 第三章: 用户表单与交互分析 (子报告B + 完整报告)
    "3": ChapterConfig(
        code="3",
        title="第三章: 用户表单与交互分析",
        word_count=6000,
        level=1,
        report_types=[ReportType.SUB_REPORT_B, ReportType.FULL_REPORT],
        prompt_template="""
基于用户的表单填写历史，撰写表单与交互分析报告(约6000字)。

表单历史: {form_history}
当前CASVE阶段: {current_casve_stage}
CASVE历史: {casve_history}

请从以下维度展开：
1. 表单填写历史回顾：追踪用户的信息完善过程
2. 数据一致性与演变：分析用户认知的变化
3. CASVE决策阶段追踪：定位当前阶段，分析阶段特征
4. 下一阶段行动建议：提供针对性的行动指导
5. 用户关注焦点识别：总结用户的核心关注点

要求：
- 体现用户的成长轨迹
- 结合CASVE循环理论
- 提供可执行的建议
- 字数控制在6000字左右
"""
    ),
    
    # 第四章: 三层职业规划结构化建模 (子报告C + 完整报告)
    "4": ChapterConfig(
        code="4",
        title="第四章: 三层职业规划结构化建模",
        word_count=15000,
        level=1,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT]
    ),
    "4.1": ChapterConfig(
        code="4.1",
        title="4.1 接口层建模: 个性化输入系统",
        word_count=4000,
        parent_code="4",
        level=2,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
基于接口层数据，构建个性化输入系统模型(约4000字)。

用户接口层数据: {interface_layer_data}

请从以下维度展开：
1. 兴趣-职业映射模型：Holland代码到职业领域的映射
2. 能力-发展潜能评估：能力矩阵与发展空间分析
3. 价值观-工作满意度预测：价值观与职业满意度关系
4. 约束条件影响分析：家庭、地域等约束的影响

要求：
- 模型化表达用户特征
- 建立量化评估体系
- 提供可视化建议
- 字数控制在4000字左右
"""
    ),
    "4.2": ChapterConfig(
        code="4.2",
        title="4.2 可变层建模: 专业适配系统",
        word_count=6000,
        parent_code="4",
        level=2,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT]
    ),
    "4.2.1": ChapterConfig(
        code="4.2.1",
        title="4.2.1 专业理论体系适配",
        word_count=2000,
        parent_code="4.2",
        level=3,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
分析用户与专业理论体系的适配性(约2000字)。

偏好专业: {preferred_majors}
用户画像: {user_profile}

请分析：
1. 基础理论模块匹配(高稳定性)
2. 应用技术模块匹配(中稳定性)
3. 前沿趋势模块匹配(低稳定性)
4. 技能半衰期分析
5. 学习路径建议
"""
    ),
    "4.2.2": ChapterConfig(
        code="4.2.2",
        title="4.2.2 职业路径分化分析",
        word_count=2000,
        parent_code="4.2",
        level=3,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
分析用户与各职业路径的匹配度(约2000字)。

用户画像: {user_profile}
路径偏好: {career_path_preference}

请分析：
1. 技术专家路径评估
2. 管理领导路径评估
3. 第三路径(产品/咨询/运营)评估
4. 公益性职业路径评估
5. 路径选择建议
"""
    ),
    "4.2.3": ChapterConfig(
        code="4.2.3",
        title="4.2.3 实践途径组合设计",
        word_count=1000,
        parent_code="4.2",
        level=3,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
设计实践途径组合方案(约1000字)。

实践经历: {practice_experiences}

请设计：
1. 竞赛参与规划
2. 项目实践规划
3. 实习体验规划
4. 学术深造规划
"""
    ),
    "4.2.4": ChapterConfig(
        code="4.2.4",
        title="4.2.4 终身学习机制规划",
        word_count=1000,
        parent_code="4.2",
        level=3,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
规划终身学习机制(约1000字)。

请规划：
1. 学习机制建立
2. 学习资源配置
3. 学习效果评估
4. 持续学习计划
"""
    ),
    "4.3": ChapterConfig(
        code="4.3",
        title="4.3 核心层建模: 跨专业能力系统",
        word_count=5000,
        parent_code="4",
        level=2,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT]
    ),
    "4.3.1": ChapterConfig(
        code="4.3.1",
        title="4.3.1 自我认知与探索方法体系",
        word_count=1200,
        parent_code="4.3",
        level=3,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
建立自我认知与探索方法体系(约1200字)。

请建立：
1. 标准化测评工具应用体系
2. 职业信息搜集框架
3. 职业探索方法组合
4. 持续自我更新机制
"""
    ),
    "4.3.2": ChapterConfig(
        code="4.3.2",
        title="4.3.2 CASVE决策加工模型",
        word_count=1200,
        parent_code="4.3",
        level=3,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
构建CASVE决策加工模型(约1200字)。

当前阶段: {current_casve_stage}
CASVE历史: {casve_history}

请构建：
1. Communication阶段方法
2. Analysis阶段方法
3. Synthesis阶段方法
4. Evaluation阶段方法
5. Execution阶段方法
6. 循环迭代机制
"""
    ),
    "4.3.3": ChapterConfig(
        code="4.3.3",
        title="4.3.3 通用技能发展矩阵",
        word_count=1300,
        parent_code="4.3",
        level=3,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
构建通用技能发展矩阵(约1300字)。

通用技能评估: {universal_skills}

请构建：
1. 沟通表达技能发展方案
2. 团队协作技能发展方案
3. 批判性思维技能发展方案
4. 创造力技能发展方案
5. 技能整合应用策略
"""
    ),
    "4.3.4": ChapterConfig(
        code="4.3.4",
        title="4.3.4 职业弹性与适应策略",
        word_count=1300,
        parent_code="4.3",
        level=3,
        report_types=[ReportType.SUB_REPORT_C, ReportType.FULL_REPORT],
        prompt_template="""
制定职业弹性与适应策略(约1300字)。

职业弹性评分: {resilience_score}

请制定：
1. 成长型思维培养方案
2. 反思能力提升方案
3. 多元网络构建方案
4. 职业转换预案
5. 逆境应对策略
"""
    ),
    
    # 第五章: 分层递进行动体系设计 (子报告D + 完整报告)
    "5": ChapterConfig(
        code="5",
        title="第五章: 分层递进行动体系设计",
        word_count=12000,
        level=1,
        report_types=[ReportType.SUB_REPORT_D, ReportType.FULL_REPORT]
    ),
    "5.1": ChapterConfig(
        code="5.1",
        title="5.1 Layer 1: 自我认知与职业探索行动计划",
        word_count=3000,
        parent_code="5",
        level=2,
        report_types=[ReportType.SUB_REPORT_D, ReportType.FULL_REPORT],
        prompt_template="""
设计Layer 1行动计划(约3000字)：自我认知与职业探索

请设计：
1. 标准化测评深化计划
   - Holland测评深化
   - MBTI测评深化
   - 能力倾向测评
   - 价值观澄清练习

2. 职业信息搜集计划
   - O*NET数据库使用
   - 行业报告研读
   - 职位描述分析

3. 实践探索行动计划
   - 信息访谈计划
   - 岗位Shadowing安排
   - 企业参访规划

要求：每个计划包含具体行动、时间安排、预期成果
"""
    ),
    "5.2": ChapterConfig(
        code="5.2",
        title="5.2 Layer 2: 核心能力构建行动计划",
        word_count=3000,
        parent_code="5",
        level=2,
        report_types=[ReportType.SUB_REPORT_D, ReportType.FULL_REPORT],
        prompt_template="""
设计Layer 2行动计划(约3000字)：核心能力构建

请设计：
1. 专业理论学习计划
   - 基础理论模块学习计划
   - 应用技术模块学习计划
   - 前沿趋势模块学习计划

2. 通用技能培养计划
   - 沟通表达训练计划
   - 团队协作训练计划
   - 批判性思维训练计划
   - 创造力训练计划

3. 自我管理能力提升计划
   - 时间管理技能
   - 情绪调节技能
   - 职业弹性培养

要求：每个计划包含具体行动、时间安排、预期成果、评估方式
"""
    ),
    "5.3": ChapterConfig(
        code="5.3",
        title="5.3 Layer 3: 实践途径多元化配置计划",
        word_count=3000,
        parent_code="5",
        level=2,
        report_types=[ReportType.SUB_REPORT_D, ReportType.FULL_REPORT],
        prompt_template="""
设计Layer 3行动计划(约3000字)：实践途径多元化配置

请设计：
1. 竞赛参与规划
   - 学科竞赛规划
   - 算法竞赛规划
   - 创新创业竞赛规划
   - 设计竞赛规划

2. 项目实践规划
   - 课程项目规划
   - 开源贡献规划
   - 个人作品规划

3. 实习体验规划
   - 探索性实习规划
   - 专业性实习规划
   - 战略性实习规划

4. 学术深造规划
   - 本科科研规划
   - 硕博连读规划
   - 博士后规划

要求：每个规划包含具体步骤、时间安排、资源需求、预期成果
"""
    ),
    "5.4": ChapterConfig(
        code="5.4",
        title="5.4 Layer 4: 终身学习系统嵌入计划",
        word_count=3000,
        parent_code="5",
        level=2,
        report_types=[ReportType.SUB_REPORT_D, ReportType.FULL_REPORT],
        prompt_template="""
设计Layer 4行动计划(约3000字)：终身学习系统嵌入

请设计：
1. 学习机制建立
   - 结构化学习机制
   - 项目驱动学习机制
   - 社区学习机制
   - 反思学习机制

2. 学习资源配置
   - 在线课程资源
   - 技术社区资源
   - 专业书籍资源
   - 会议活动资源

3. 学习效果评估体系
   - 知识掌握评估
   - 技能发展评估
   - 能力提升评估
   - 成果产出评估

要求：每个计划包含具体机制、资源配置、评估标准、持续改进方案
"""
    ),
    
    # 第六章: 职业发展路径推荐 (仅完整报告)
    "6": ChapterConfig(
        code="6",
        title="第六章: 职业发展路径推荐",
        word_count=4000,
        level=1,
        report_types=[ReportType.FULL_REPORT],
        prompt_template="""
基于用户画像和三层模型，推荐职业发展路径(约4000字)。

用户画像: {user_profile}
三层模型: {three_layer_model}

请推荐：
1. 短期路径(1-2年)
   - 阶段目标
   - 关键行动
   - 预期成果
   - 里程碑节点

2. 中期路径(3-5年)
   - 阶段目标
   - 关键行动
   - 预期成果
   - 里程碑节点

3. 长期路径(5-10年)
   - 阶段目标
   - 关键行动
   - 预期成果
   - 里程碑节点

4. 路径切换预案
   - 切换触发条件
   - 切换准备方案
   - 切换执行步骤

要求：路径具体可行，包含量化指标和时间节点
"""
    ),
    
    # 第七章: 风险评估与应对策略 (仅完整报告)
    "7": ChapterConfig(
        code="7",
        title="第七章: 风险评估与应对策略",
        word_count=2500,
        level=1,
        report_types=[ReportType.FULL_REPORT],
        prompt_template="""
进行风险评估并制定应对策略(约2500字)。

请分析：
1. 内部风险识别
   - 能力短板风险
   - 决策失误风险
   - 执行力不足风险
   - 心态波动风险

2. 外部风险识别
   - 行业变化风险
   - 技术变革风险
   - 就业市场风险
   - 政策环境风险

3. 应对策略与预案
   - 风险预防措施
   - 风险监控机制
   - 应急响应预案
   - 损失控制方案

要求：风险识别全面，应对策略具体可行
"""
    ),
    
    # 第八章: 附录 (仅完整报告)
    "8": ChapterConfig(
        code="8",
        title="第八章: 附录",
        word_count=2000,
        level=1,
        report_types=[ReportType.FULL_REPORT],
        prompt_template="""
编写附录内容(约2000字)：

1. 参考文献与资源
   - 引用的理论文献
   - 推荐的学习资源
   - 有用的工具和网站

2. 专业术语表
   - Holland代码解释
   - MBTI术语解释
   - 职业规划专业术语

3. 工具与模板
   - CASVE决策记录模板
   - 能力提升跟踪表
   - 目标分解模板

4. 报告生成元数据
   - 生成时间
   - 数据版本
   - 使用模型信息
"""
    )
}


# ==================== 报告生成服务 ====================

class ReportGenerationService:
    """
    报告生成服务
    
    使用LazyLLM实现并行章节生成
    """
    
    def __init__(self, db: Session):
        self.db = db
        # TODO: 初始化LazyLLM模块
        # self.llm = OnlineChatModule(model="kimi", stream=True)
    
    async def generate_report(
        self,
        user_id: str,
        report_type: ReportType,
        options: Optional[GenerationOptions] = None
    ) -> str:
        """
        生成报告
        
        Returns:
            task_id: 生成任务ID
        """
        # 1. 创建报告记录
        report_title = self._get_report_title(report_type)
        report = create_user_report(self.db, UserReportCreate(
            user_id=user_id,
            title=report_title,
            report_type=report_type,
            detail_level=options.detail_level if options else "detailed",
            include_charts=options.include_charts if options else True,
            language=options.language if options else "zh-CN"
        ))
        
        # 2. 创建生成任务
        task = create_generation_task(self.db, GenerationTaskCreate(
            user_id=user_id,
            report_type=report_type,
            report_id=report.id,
            options=options
        ))
        
        # 3. 创建章节记录
        chapter_configs = self._get_chapter_configs(report_type)
        for config in chapter_configs:
            create_report_chapter(self.db, ReportChapterCreate(
                report_id=report.id,
                chapter_code=config.code,
                title=config.title,
                parent_id=self._get_parent_chapter_id(report.id, config.parent_code),
                order_num=self._get_order_num(config.code),
                level=config.level,
                status=ChapterStatus.PENDING
            ))
        
        # 4. 启动异步生成流程
        asyncio.create_task(self._run_generation_workflow(task.id, report.id, user_id))
        
        return task.id
    
    async def _run_generation_workflow(
        self,
        task_id: str,
        report_id: str,
        user_id: str
    ):
        """运行生成工作流"""
        try:
            # 更新任务状态
            update_generation_task(
                self.db, task_id,
                status=TaskStatus.GENERATING,
                started_at=datetime.utcnow()
            )
            
            # 获取用户数据
            user_data = self._fetch_user_data(user_id)
            
            # 创建数据快照
            self._create_data_snapshots(report_id, user_id, user_data)
            
            # 获取章节列表
            chapters = self._get_pending_chapters(report_id)
            
            # 更新总章节数
            update_generation_task(
                self.db, task_id,
                total_chapters=len(chapters)
            )
            
            # TODO: 使用LazyLLM并行生成章节
            # 由于LazyLLM依赖复杂，这里先使用串行模拟
            for i, chapter in enumerate(chapters):
                await self._generate_chapter(task_id, chapter, user_data, i, len(chapters))
            
            # 组装报告
            update_generation_task(
                self.db, task_id,
                status=TaskStatus.ASSEMBLING,
                current_stage="content_assembly"
            )
            await self._assemble_report(report_id)
            
            # 更新报告状态
            total_word_count = self._calculate_total_word_count(report_id)
            chapter_count = len(chapters)
            
            update_user_report(self.db, report_id, UserReportUpdate(
                status=ReportStatus.COMPLETED,
                word_count=total_word_count,
                chapter_count=chapter_count,
                completed_at=datetime.utcnow()
            ))
            
            # 完成任务
            update_generation_task(
                self.db, task_id,
                status=TaskStatus.COMPLETED,
                progress=100,
                completed_at=datetime.utcnow()
            )
            
        except Exception as e:
            # 记录错误
            create_generation_log(
                self.db, task_id,
                message=f"Generation failed: {str(e)}",
                log_level="error"
            )
            
            # 更新任务状态为失败
            update_generation_task(
                self.db, task_id,
                status=TaskStatus.FAILED,
                error_code="GENERATION_ERROR",
                error_message=str(e)
            )
            
            # 更新报告状态
            update_user_report(self.db, report_id, UserReportUpdate(
                status=ReportStatus.FAILED
            ))
    
    async def _generate_chapter(
        self,
        task_id: str,
        chapter: ReportChapter,
        user_data: Dict,
        index: int,
        total: int
    ):
        """生成单个章节"""
        start_time = datetime.utcnow()
        
        # 更新当前章节
        update_generation_task(
            self.db, task_id,
            current_chapter_id=chapter.id,
            current_stage="chapter_generation"
        )
        
        # 更新章节状态
        update_chapter_content(
            self.db, chapter.id,
            status=ChapterStatus.GENERATING
        )
        
        # 获取章节配置
        config = CHAPTER_CONFIGS.get(chapter.chapter_code)
        
        try:
            # TODO: 调用LazyLLM生成内容
            # 这里使用模拟生成
            content = await self._mock_generate_chapter(chapter, user_data, config)
            
            # 计算字数
            word_count = len(content)
            
            # 更新章节内容
            end_time = datetime.utcnow()
            generation_time = int((end_time - start_time).total_seconds())
            
            update_chapter_content(
                self.db, chapter.id,
                content_html=f"<div class='chapter'>{content}</div>",
                content_markdown=content,
                content_plain=content,
                word_count=word_count,
                status=ChapterStatus.COMPLETED,
                generation_time=generation_time,
                llm_model="kimi-mock"
            )
            
            # 更新进度
            progress = int((index + 1) / total * 80)  # 生成占80%进度
            update_generation_task(
                self.db, task_id,
                progress=progress,
                completed_chapters=index + 1
            )
            
            # 记录日志
            create_generation_log(
                self.db, task_id,
                message=f"Chapter {chapter.chapter_code} generated successfully",
                stage="chapter_generation",
                chapter_id=chapter.id,
                details={"word_count": word_count, "generation_time": generation_time}
            )
            
        except Exception as e:
            # 更新章节状态为失败
            update_chapter_content(
                self.db, chapter.id,
                status=ChapterStatus.FAILED
            )
            
            # 记录错误日志
            create_generation_log(
                self.db, task_id,
                message=f"Chapter {chapter.chapter_code} generation failed: {str(e)}",
                log_level="error",
                stage="chapter_generation",
                chapter_id=chapter.id
            )
            
            raise
    
    async def _mock_generate_chapter(
        self,
        chapter: ReportChapter,
        user_data: Dict,
        config: Optional[ChapterConfig]
    ) -> str:
        """
        模拟章节生成
        
        实际实现中，这里应该调用LazyLLM进行生成
        """
        # 模拟延迟
        await asyncio.sleep(1)
        
        # 生成模拟内容
        config_word_count = config.word_count if config else 1000
        
        # 构建提示词
        prompt = self._build_prompt(config, user_data) if config else f"生成{chapter.title}"
        
        # TODO: 调用LazyLLM
        # content = await self.llm(prompt)
        
        # 模拟内容
        content = f"""
# {chapter.title}

这是{chapter.title}的模拟生成内容。实际实现中将使用LazyLLM基于以下提示词生成：

```
{prompt[:500]}...
```

(此处省略约{config_word_count}字的内容...)

## 关键要点

1. 基于用户画像数据深度分析
2. 结合Career-Planning三层模型理论
3. 提供具体可行的建议
4. 符合职业规划专业规范

## 总结

本章节详细分析了用户的{chapter.title}相关内容，为后续职业规划提供了基础。
        """.strip()
        
        return content
    
    def _build_prompt(self, config: ChapterConfig, user_data: Dict) -> str:
        """构建生成提示词"""
        if not config.prompt_template:
            return f"请撰写关于{config.title}的内容，约{config.word_count}字。"
        
        try:
            return config.prompt_template.format(**user_data)
        except KeyError:
            # 如果格式化失败，返回模板本身
            return config.prompt_template
    
    async def _assemble_report(self, report_id: str):
        """组装报告"""
        # 获取所有章节
        chapters = self._get_chapters_by_report(report_id)
        
        # 按顺序组装内容
        assembled_content = []
        for chapter in sorted(chapters, key=lambda c: c.order_num):
            if chapter.content_markdown:
                assembled_content.append(chapter.content_markdown)
        
        # TODO: 保存组装后的完整报告
        # 可以存储到文件系统或数据库
    
    def _get_report_title(self, report_type: ReportType) -> str:
        """获取报告标题"""
        titles = {
            ReportType.SUB_REPORT_A: "用户画像深度分析报告",
            ReportType.SUB_REPORT_B: "用户表单分析报告",
            ReportType.SUB_REPORT_C: "三层职业规划建模报告",
            ReportType.SUB_REPORT_D: "分层递进行动体系报告",
            ReportType.FULL_REPORT: "职业规划完整报告"
        }
        return titles.get(report_type, "职业规划报告")
    
    def _get_chapter_configs(self, report_type: ReportType) -> List[ChapterConfig]:
        """获取章节配置列表"""
        return [
            config for config in CHAPTER_CONFIGS.values()
            if report_type in config.report_types
        ]
    
    def _get_parent_chapter_id(self, report_id: str, parent_code: Optional[str]) -> Optional[str]:
        """获取父章节ID"""
        if not parent_code:
            return None
        
        chapter = self.db.query(ReportChapter).filter(
            ReportChapter.report_id == report_id,
            ReportChapter.chapter_code == parent_code
        ).first()
        
        return chapter.id if chapter else None
    
    def _get_order_num(self, code: str) -> int:
        """获取排序序号"""
        # 简单的排序逻辑：基于章节代码
        parts = code.split('.')
        order = 0
        for i, part in enumerate(parts):
            order += int(part) * (100 ** (3 - i))
        return order
    
    def _fetch_user_data(self, user_id: str) -> Dict:
        """获取用户数据"""
        from .crud_user_profile import get_user_profile
        from .crud_user_report import get_generation_logs
        
        profile = get_user_profile(self.db, user_id)
        
        # 获取表单提交次数
        form_logs_count = self.db.query(GenerationLog).filter(
            GenerationLog.task_id.in_(
                self.db.query(GenerationTask.id).filter(
                    GenerationTask.user_id == user_id
                )
            )
        ).count()
        
        return {
            "user_id": user_id,
            "holland_code": profile.holland_code if profile else None,
            "mbti_type": profile.mbti_type if profile else None,
            "value_priorities": profile.value_priorities if profile else [],
            "ability_assessment": profile.ability_assessment if profile else {},
            "career_path_preference": profile.career_path_preference if profile else None,
            "current_casve_stage": profile.current_casve_stage if profile else None,
            "casve_history": profile.casve_history if profile else [],
            "universal_skills": profile.universal_skills if profile else {},
            "resilience_score": profile.resilience_score if profile else None,
            "preferred_disciplines": profile.preferred_disciplines if profile else [],
            "preferred_majors": profile.preferred_majors if profile else [],
            "practice_experiences": profile.practice_experiences if profile else [],
            "constraints": profile.constraints if profile else {},
            "completeness_score": profile.completeness_score if profile else 0,
            "form_submission_count": form_logs_count
        }
    
    def _create_data_snapshots(self, report_id: str, user_id: str, user_data: Dict):
        """创建数据快照"""
        # 接口层快照
        create_report_snapshot(
            self.db, report_id, user_id, "interface_layer",
            {
                "holland_code": user_data["holland_code"],
                "mbti_type": user_data["mbti_type"],
                "value_priorities": user_data["value_priorities"],
                "ability_assessment": user_data["ability_assessment"],
                "constraints": user_data["constraints"]
            }
        )
        
        # 可变层快照
        create_report_snapshot(
            self.db, report_id, user_id, "variable_layer",
            {
                "preferred_disciplines": user_data["preferred_disciplines"],
                "preferred_majors": user_data["preferred_majors"],
                "career_path_preference": user_data["career_path_preference"],
                "practice_experiences": user_data["practice_experiences"]
            }
        )
        
        # 核心层快照
        create_report_snapshot(
            self.db, report_id, user_id, "core_layer",
            {
                "current_casve_stage": user_data["current_casve_stage"],
                "casve_history": user_data["casve_history"],
                "universal_skills": user_data["universal_skills"],
                "resilience_score": user_data["resilience_score"]
            }
        )
    
    def _get_pending_chapters(self, report_id: str) -> List[ReportChapter]:
        """获取待生成的章节列表"""
        return self.db.query(ReportChapter).filter(
            ReportChapter.report_id == report_id
        ).order_by(ReportChapter.order_num).all()
    
    def _get_chapters_by_report(self, report_id: str) -> List[ReportChapter]:
        """获取报告的所有章节"""
        return self.db.query(ReportChapter).filter(
            ReportChapter.report_id == report_id
        ).all()
    
    def _calculate_total_word_count(self, report_id: str) -> int:
        """计算报告总字数"""
        from sqlalchemy import func
        
        result = self.db.query(func.sum(ReportChapter.word_count)).filter(
            ReportChapter.report_id == report_id
        ).scalar()
        
        return result or 0
