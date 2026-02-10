# Career-Planning Skill

## Metadata
- **Version**: 1.1
- **Last Updated**: 2025-01
- **Source**: 基于《大学生职业规划结构化建模》研究报告整理
- **Original Doc**: [references/职业生涯规划.pdf](./references/职业生涯规划.pdf)

## Description
职业规划理论、职业道路选择模式、职业路径分化与进阶、职业规划的结构化模型、职业行动计划与实践建议、专家建议、行业趋势

---

## Core Architecture: 三层职业规划结构化模型

> **项目关键参考**：本架构是职业路径图功能开发的核心依据

```
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: 接口层 (Interface Layer) - 个性化输入                           │
├─────────────────────────────────────────────────────────────────────────┤
│ 输入维度                                                                  │
│ ├── 个人兴趣与价值观 (Interest & Values)                                   │
│ │   └── 参考: [03-career-path-selection.md](./references/03-career-path-selection.md)
│ ├── 能力优势与发展空间 (Ability & Potential)                               │
│ │   └── 参考: [04-career-progression.md](./references/04-career-progression.md)
│ ├── 家庭背景与资源 (Family Background & Resources)                         │
│ └── 生活目标与约束 (Life Goals & Constraints)                              │
│                                                                          │
│ 应用: 用户画像构建、个性化推荐、职业匹配度计算                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: 可变层 (Variable Layer) - 专业适配要素                          │
├─────────────────────────────────────────────────────────────────────────┤
│ 模块 2.1: 专业理论体系 (Professional Theory System)                        │
│ ├── 基础理论模块 (高稳定性, λ≈0.03, 半衰期~23年)                          │
│ │   └── 参考: [02-lifelong-learning.md#基础理论模块](./references/02-lifelong-learning.md)
│ ├── 应用技术模块 (中稳定性, λ≈0.15, 半衰期~4.6年)                         │
│ │   └── 参考: [02-lifelong-learning.md#应用技术模块](./references/02-lifelong-learning.md)
│ └── 前沿趋势模块 (低稳定性, λ≈0.35, 半衰期~2年)                           │
│     └── 参考: [02-lifelong-learning.md#前沿趋势模块](./references/02-lifelong-learning.md)
│                                                                          │
│ 模块 2.2: 职业路径分化 (Career Path Differentiation)                       │
│ ├── 技术专家路径 (Technical Expert)                                        │
│ ├── 管理领导路径 (Management Leader)                                       │
│ ├── 第三路径 (产品/咨询/运营等)                                            │
│ └── 公益性职业路径 (Public Welfare)                                        │
│     └── 详细: [04-career-progression.md](./references/04-career-progression.md)
│                                                                          │
│ 模块 2.3: 实践途径组合 (Practice Pathway Combination)                      │
│ ├── 竞赛参与 (Competition) - 能力验证与网络构建                            │
│ ├── 项目实践 (Project) - 课程/开源/个人作品                                │
│ ├── 实习体验 (Internship) - 探索性/专业性/战略性                           │
│ └── 学术深造 (Academic) - 本科科研/硕博/博士后                             │
│     └── 详细: [05-action-plan.md#第三层](./references/05-action-plan.md)
│                                                                          │
│ 模块 2.4: 终身学习机制 (Lifelong Learning Mechanism)                       │
│ ├── 学习机制建立 (Learning System)                                         │
│ ├── 学习资源配置 (Resource Allocation)                                     │
│ └── 学习效果评估 (Outcome Assessment)                                      │
│     └── 详细: [02-lifelong-learning.md](./references/02-lifelong-learning.md)
│                                                                          │
│ 应用: 专业适配、路径推荐、能力模型构建、学习路径规划                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: 核心层 (Core Layer) - 跨专业不变要素                            │
├─────────────────────────────────────────────────────────────────────────┤
│ 要素 1.1: 自我认知与职业探索方法                                           │
│ ├── 标准化测评工具 (Holland/MBTI/能力倾向/价值观)                          │
│ │   └── 详细: [01-theoretical-foundations.md#标准化测评工具](./references/01-theoretical-foundations.md)
│ ├── 职业信息搜集框架 (O*NET/职位描述/行业报告)                             │
│ └── 职业探索方法 (信息访谈/岗位Shadowing/企业参访)                         │
│     └── 详细: [03-career-path-selection.md#职业探索方法工具箱](./references/03-career-path-selection.md)
│                                                                          │
│ 要素 1.2: 决策加工与执行保障 (CASVE Cycle)                                 │
│ ├── C - Communication (沟通): 识别决策需求                                  │
│ ├── A - Analysis (分析): 系统梳理自我与选项                                 │
│ ├── S - Synthesis (综合): 生成可能方案                                      │
│ ├── V - Evaluation (评估): 权衡各选项优劣                                   │
│ └── E - Execution (执行): 将选择转化为行动                                  │
│     └── 详细: [01-theoretical-foundations.md#CASVE循环详解](./references/01-theoretical-foundations.md)
│                                                                          │
│ 要素 1.3: 通用技能发展矩阵 (Universal Skills Matrix)                        │
│ ├── 沟通表达 (Communication)                                               │
│ ├── 团队协作 (Collaboration)                                               │
│ ├── 批判性思维 (Critical Thinking)                                         │
│ └── 创造力 (Creativity)                                                    │
│     └── 详细: [04-career-progression.md#通用技能矩阵](./references/04-career-progression.md)
│                                                                          │
│ 要素 1.4: 职业弹性与适应策略 (Career Resilience)                           │
│ ├── 成长型思维 (Growth Mindset)                                            │
│ ├── 反思能力 (Reflective Capacity)                                         │
│ └── 多元网络 (Diverse Network)                                             │
│     └── 详细: [04-career-progression.md#职业弹性](./references/04-career-progression.md)
│                                                                          │
│ 应用: 基础能力培养、决策支持系统、通用训练模块                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Hierarchical Action System: 分层递进行动体系

> 实施三层模型的具体操作框架

```
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: 终身学习系统嵌入                                                │
│ ├── 学习机制: 结构化学习/项目驱动/社区学习/反思学习                         │
│ ├── 资源配置: 在线课程/技术社区/专业书籍/会议活动                           │
│ └── 效果评估: 知识掌握/技能发展/能力提升/成果产出                           │
│     └── 参考: [05-action-plan.md#第四层](./references/05-action-plan.md)
├─────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: 实践途径多元化配置                                               │
│ ├── 竞赛参与: 学科竞赛/算法竞赛/创新创业/设计竞赛                           │
│ ├── 项目实践: 课程项目 → 开源贡献 → 个人作品                               │
│ ├── 实习体验: 探索性 → 专业性 → 战略性                                     │
│ └── 学术深造: 本科科研 → 硕博连读 → 博士后                                 │
│     └── 参考: [05-action-plan.md#第三层](./references/05-action-plan.md)
├─────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: 核心能力构建层                                                   │
│ ├── 专业理论: 基础模块(高稳定) + 应用模块(中稳定) + 前沿模块(低稳定)         │
│ ├── 通用技能: 沟通/协作/批判思维/创造力                                    │
│ └── 自我管理: 时间管理/情绪调节/职业弹性                                   │
│     └── 参考: [05-action-plan.md#第二层](./references/05-action-plan.md)
├─────────────────────────────────────────────────────────────────────────┤
│ LAYER 1: 自我认知与职业探索层                                             │
│ ├── 标准化测评: Holland/MBTI/能力倾向/价值观                               │
│ ├── 职业信息: 工作内容/能力要求/发展前景/工作环境                          │
│ └── 实践探索: 信息访谈/岗位Shadowing/企业参访                              │
│     └── 参考: [05-action-plan.md#第一层](./references/05-action-plan.md)
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### 三大职业选择模式

| 模式 | 驱动因素 | 适合人群 | 风险 | 参考文档 |
|------|----------|----------|------|----------|
| **内生驱动型** | 兴趣与价值观 | 追求意义感 | 可能与市场需求脱节 | [03-career-path-selection.md#内生驱动型](./references/03-career-path-selection.md) |
| **外生适应型** | 就业趋势与市场需求 | 追求稳定性 | 工作动力可能不足 | [03-career-path-selection.md#外生适应型](./references/03-career-path-selection.md) |
| **使命驱动型** | 社会贡献与公共价值 | 追求超越个人利益 | 物质回报可能较低 | [03-career-path-selection.md#使命驱动型](./references/03-career-path-selection.md) |

### 三大职业进阶路径

| 路径 | 核心特征 | 发展阶段 | 成功标志 | 参考文档 |
|------|----------|----------|----------|----------|
| **技术专家** | 深耕专业技术 | 初级→中级→高级→专家 | 技术深度、行业声誉 | [04-career-progression.md#技术专家路径](./references/04-career-progression.md) |
| **管理领导** | 领导团队达成目标 | 组长→经理→总监→高管 | 团队规模、业务成果 | [04-career-progression.md#管理领导路径](./references/04-career-progression.md) |
| **第三路径** | 产品/咨询/运营专业化 | 专员→专家→资深→首席 | 专业影响力、综合能力 | [04-career-progression.md#第三路径](./references/04-career-progression.md) |

### CASVE 决策循环

```
[Communication] 识别决策需求 → [Analysis] 系统梳理信息 → [Synthesis] 生成方案
        ↑                                                                      ↓
[Execution] 转化为行动 ← [Evaluation] 权衡评估 ←
        ↑________________________(迭代)________________________↓
```

**各阶段关键行动**:
- **C**: 生涯幻游、不满来源分析
- **A**: SWOT分析、决策矩阵
- **S**: 头脑风暴、选项扩展
- **V**: 多标准决策分析、情景规划
- **E**: 目标分解、时间表制定

详细: [01-theoretical-foundations.md#CASVE循环详解](./references/01-theoretical-foundations.md)

---

## Key Theories & Models

### 1. 认知信息加工理论 (CIP)
- **知识领域**: 自我知识 + 职业知识
- **决策领域**: CASVE循环
- **执行领域**: 自我对话、自我意识、自我监控
- 参考: [01-theoretical-foundations.md#认知信息加工理论](./references/01-theoretical-foundations.md)

### 2. 技能半衰期模型
```
V(t) = V₀ · e^(-λt)
```
- 前端技术: λ=0.35, 半衰期~2年
- 后端技术: λ=0.15, 半衰期~4.6年
- 算法基础: λ=0.03, 半衰期~23年
- 参考: [01-theoretical-foundations.md#技能半衰期模型](./references/01-theoretical-foundations.md)

### 3. 舒伯生涯发展阶段论
| 阶段 | 年龄 | 核心任务 | 大学生关联 |
|------|------|----------|------------|
| 探索阶段 | 15-24岁 | 职业选择、教育培训、就业体验 | 核心阶段 |
| 建立阶段 | 25-44岁 | 职业稳定、成就追求 | 未来展望 |
- 参考: [01-theoretical-foundations.md#舒伯生涯发展阶段论](./references/01-theoretical-foundations.md)

### 4. 终身学习理论
- 定位: 连接理论与实践的"元认知桥梁"
- 量化指标: 每周5小时结构化学习 / 每季度1项新技术 / 每年1个跨领域项目
- 参考: [02-lifelong-learning.md](./references/02-lifelong-learning.md)

---

## Reference Documents

| # | 文档 | 主要内容 | 适用场景 |
|---|------|----------|----------|
| 01 | [theoretical-foundations.md](./references/01-theoretical-foundations.md) | CIP理论、人职匹配、职业发展理论、技能半衰期、知识复利、学习ROI | 理论框架理解 |
| 02 | [lifelong-learning.md](./references/02-lifelong-learning.md) | 终身学习定位、模块化学习策略、跨专业框架 | 学习系统设计 |
| 03 | [career-path-selection.md](./references/03-career-path-selection.md) | 三大选择模式、探索方法、职业访谈、跨专业迁移 | 职业探索阶段 |
| 04 | [career-progression.md](./references/04-career-progression.md) | 三大进阶路径、职业转换、能力矩阵、职业弹性 | 路径规划阶段 |
| 05 | [action-plan.md](./references/05-action-plan.md) | 分层行动体系、实践途径、行动计划模板 | 执行实施阶段 |
| 06 | [industry-trends.md](./references/06-industry-trends.md) | 专家建议、热门行业、薪资结构、行动检查清单 | 决策支持 |

---

## Application Scenarios

### 场景 1: 职业路径图功能开发
```
输入: 用户画像 (接口层)
  ↓
处理: 专业适配计算 (可变层)
  - 专业理论体系匹配
  - 职业路径推荐
  - 实践途径组合
  ↓
输出: 个性化职业路径图 + 行动计划 (整合三层)
  ↓
支撑: 核心层通用模块 (测评/CASVE/技能培养)
```

### 场景 2: 职业规划咨询
1. **评估阶段**: 使用接口层输入 → 自我认知测评
2. **分析阶段**: 应用核心层 → CASVE决策分析
3. **规划阶段**: 配置可变层 → 专业适配、路径选择
4. **执行阶段**: 实施分层行动体系

### 场景 3: 专业与职业匹配
- 基础: 核心层通用框架
- 变量: 可变层专业适配要素
- 个性化: 接口层用户输入

---

## Implementation Notes for Developers

### 数据库设计建议
```
Interface Layer (用户画像表)
├── user_id
├── interest_profile (Holland代码)
├── ability_assessment
├── values_priority
└── constraints (家庭/生活)

Variable Layer (专业适配表)
├── discipline_id (学科)
├── major_category_id (专业类)
├── theory_modules (理论模块JSON)
├── career_paths (路径选项JSON)
└── practice_pathways (实践途径JSON)

Core Layer (核心要素表)
├── assessment_tools (测评工具)
├── casve_templates (决策模板)
├── skill_matrix (技能矩阵)
└── resilience_resources (弹性资源)
```

### API 设计建议
```
GET /api/career/path-recommendation
  Input: user_profile (接口层)
  Logic: match_variable_layer (可变层匹配)
  Output: recommended_paths + action_plan

POST /api/career/casve-decision
  Input: current_stage + user_data
  Logic: core_layer_casve_process
  Output: next_stage + action_items
```

---

## Original Reference
- [职业生涯规划.pdf](./references/职业生涯规划.pdf) - 大学生职业规划结构化建模研究报告 (47页)
