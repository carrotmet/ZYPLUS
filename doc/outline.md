# 职业规划网站项目大纲

## 项目概述

**项目名称**: 职业规划导航平台  
**项目路径**: `D:\github.com\carrotmet\zyplusv2`  
**项目类型**: 前后端分离的Web应用  
**目标用户**: 高中生和大学生

## 项目结构

```
D:\github.com\carrotmet\zyplusv2\
├── 📁 backend/                    # 后端代码目录
│   ├── 📁 app/                   # FastAPI应用代码
│   │   ├── 📄 __init__.py       # 应用初始化
│   │   ├── 📄 crud.py           # 数据库CRUD操作
│   │   ├── 📄 database.py       # 数据库连接和配置
│   │   ├── 📄 main.py           # FastAPI主应用入口
│   │   ├── 📄 models.py         # SQLAlchemy数据模型
│   │   ├── 📄 schemas.py        # Pydantic数据验证模型
│   │   └── 📄 setup_database.py # 数据库设置脚本
│   ├── 📄 Dockerfile            # 后端Docker镜像配置
│   └── 📄 requirements.txt      # Python依赖包列表
│
├── 📁 backup/                    # 代码备份目录
│   └── 📁 backend_app_20260128/ # 2026年1月28日的代码备份
│       ├── 📄 crud.py
│       ├── 📄 database.py
│       ├── 📄 main.py
│       └── 📄 schemas.py
│
├── 📁 data/                      # 数据目录
│   └── 📄 career_guidance.db    # SQLite数据库文件
│
├── 📁 doc/                       # 项目文档目录
│   ├── 📄 DATABASE_SETUP.md     # 数据库设置说明
│   ├── 📄 design.md             # API设计文档
│   ├── 📄 DEVELOPMENT_SUMMARY.md # 开发总结
│   ├── 📄 FINAL_SUMMARY.md      # 最终完成总结
│   ├── 📄 INDEX_HTML_REFACTOR.md.old # 废弃的重构文档
│   ├── 📄 INDEX_HTML_ROLLBACK.md # 回退记录
│   ├── 📄 INSTALLATION.md       # 安装指南
│   ├── 📄 interaction.md        # 交互设计文档
│   ├── 📄 MODIFICATIONS.md      # 修改记录
│   ├── 📄 outline.md            # 项目大纲（本文档）
│   ├── 📄 PROJECT_COMPLETION.md # 项目完成报告
│   ├── 📄 UPDATE_LOG_20260128.md # 2026年1月28日更新日志
│   ├── 📄 WINDOWS_DEVELOPMENT.md # Windows开发指南
│   ├── 📄 代码问题报告.md       # 代码问题报告
│   └── 📄 修改报告.md           # 代码修复报告
│
├── 📁 logs/                      # 日志目录
│
├── 📁 resources/                 # 静态资源目录
│   ├── 📄 career-abstract.jpg   # 职业抽象图
│   ├── 📄 hero-bg.jpg           # 主页背景图
│   ├── 📄 student-avatar1.jpg   # 学生头像1
│   └── 📄 student-avatar2.jpg   # 学生头像2
│
├── 📁 temp/                      # 测试文件目录
│   ├── 📄 fix_db.py             # 数据库修复脚本
│   ├── 📄 fix_db_import.py      # 数据库导入修复
│   ├── 📄 test-api.py           # API测试脚本
│   ├── 📄 test_init.py          # 初始化测试
│   └── 📄 verify_db.py          # 数据库验证脚本
│
├── 📁 trash/                     # 废弃文件目录
│   ├── 📄 start-backend.bat.old
│   ├── 📄 start-dev.bat.old
│   └── 📄 start-frontend.bat.old
│
├── 📄 add-info.html             # 信息管理页面
├── 📄 add-info.js               # 信息管理页面逻辑
├── 📄 api-service.js            # API服务封装
├── 📄 docker-compose.yml        # Docker Compose配置
├── 📄 Dockerfile                # 前端Docker镜像配置
├── 📄 experience-sharing.html   # 经历分享页面
├── 📄 index.html                # 主页 - 专业选择界面
├── 📄 main.js                   # 主页逻辑
├── 📄 major-detail.html         # 专业详情页 - 职业信息展示
├── 📄 nginx.conf                # Nginx配置文件
├── 📄 README.md                 # 项目说明文档
├── 📄 setup-database.bat        # 数据库初始化脚本
├── 📄 start.sh                  # Linux/Mac启动脚本
├── 📄 start-backend.bat         # Windows后端启动脚本
├── 📄 start-dev.bat             # Windows开发环境启动脚本
└── 📄 start-frontend.bat        # Windows前端启动脚本
```

## 页面功能规划

### 1. index.html - 主页专业选择界面
**设计风格**: 现代简约，水鸟色系配色  
**主要功能**:
- 导航栏: 网站logo、主要页面链接、搜索框
- 简洁的hero区域: 网站介绍和背景图
- 核心交互区域:
  - 左侧: 专业树形导航（学科门类 → 专业类 → 具体专业）
  - 右侧: 选中专业的预览卡片
- 热门专业推荐区域
- 页脚: 版权信息

**交互组件**:
- MajorTree: 可展开收缩的树形导航
- SearchBox: 实时搜索专业
- MajorCard: 专业信息卡片展示

### 2. major-detail.html - 专业详情页
**设计风格**: 数据驱动的专业展示页面  
**主要功能**:
- 导航栏: 返回主页、搜索功能
- 专业基本信息区域: 专业名称、简介、学制等
- 职业路径可视化区域:
  - 相关职业卡片网格
  - 职业发展路径图表（ECharts流程图）
  - 薪资趋势线图
- 专业课程信息
- 相关推荐专业

**交互组件**:
- OccupationCard: 职业信息卡片
- CareerPathChart: 职业发展路径可视化
- SalaryChart: 薪资趋势图表
- RecommendationSlider: 推荐专业滑动展示

### 3. add-info.html - 信息管理页
**设计风格**: 简洁的表单页面  
**主要功能**:
- 导航栏: 返回主页
- 功能选择区域: 添加专业 / 添加职业 / 添加个人经历
- 表单区域:
  - 添加专业表单: 名称、分类、描述、学制、课程
  - 添加职业表单: 名称、行业、描述、要求、薪资范围
  - 添加个人经历表单: 昵称、专业、学历、学校、学位、经历
- 提交结果预览
- 新增信息显示: 提交后立即在相应界面显示

**交互组件**:
- FormToggle: 切换添加类型
- MajorForm: 专业信息表单
- OccupationForm: 职业信息表单
- ExperienceForm: 个人经历表单
- PreviewCard: 实时预览卡片
- DynamicUpdater: 动态UI更新组件

### 4. experience-sharing.html - 经历分享页面（新增）
**设计风格**: 社区式分享页面  
**主要功能**:
- 导航栏: 网站logo、主要页面链接
- 经历列表展示: 以卡片形式展示所有个人经历
- 筛选功能: 按专业、学历、时间筛选
- 搜索功能: 按关键词搜索经历内容
- 经历详情: 点击卡片查看详细经历
- 经验分享: 相关经验分享和讨论

**交互组件**:
- ExperienceCard: 个人经历卡片
- FilterPanel: 筛选面板
- SearchBox: 搜索框
- ExperienceDetail: 经历详情展示
- ShareComponent: 经验分享组件

## 后端架构

### 技术栈
- **框架**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **数据库**: SQLite
- **验证**: Pydantic
- **服务器**: Uvicorn

### 核心模块
| 文件 | 功能 |
|------|------|
| main.py | FastAPI应用入口，路由定义 |
| database.py | 数据库连接、会话管理 |
| models.py | SQLAlchemy数据模型定义 |
| schemas.py | Pydantic数据验证模型 |
| crud.py | 数据库CRUD操作封装 |

### 数据表结构
1. **disciplines** - 学科门类表
2. **major_categories** - 专业类表
3. **majors** - 专业表
4. **occupations** - 职业表
5. **major_occupations** - 专业职业关联表
6. **career_paths** - 职业路径表
7. **personal_experiences** - 个人经历表
8. **experience_shares** - 经验分享表

## 前端技术栈

- **基础**: HTML5 + CSS3 + JavaScript ES6+
- **样式框架**: Tailwind CSS（快速响应式设计）
- **动画库**: Anime.js（页面过渡和微交互）
- **图表库**: ECharts.js（职业路径和薪资可视化）
- **图标**: Font Awesome（统一图标系统）

## 启动脚本说明

| 脚本文件 | 功能 | 适用环境 |
|----------|------|----------|
| start.sh | 一键启动前后端服务 | Linux/Mac |
| start-dev.bat | 开发环境菜单（启动后端/前端/全部） | Windows |
| start-backend.bat | 启动后端服务 | Windows |
| start-frontend.bat | 启动前端服务 | Windows |
| setup-database.bat | 初始化数据库 | Windows |

## 响应式设计

- **桌面端** (>1024px): 左侧导航 + 右侧内容的三栏布局
- **平板端** (768px-1024px): 可收缩侧边栏的两栏布局  
- **移动端** (<768px): 单栏布局，底部导航

## 视觉设计

- **配色方案**: 水鸟色系（#4A90E4, #7BB3F0, #A8C8EC, #D6E3F8）
- **字体选择**: 标题使用Noto Serif SC，正文使用Noto Sans SC
- **布局原则**: 卡片式设计，充足的留白，清晰的信息层级

## 开发优先级

### 第一阶段（核心功能）
1. 创建主页专业选择器界面
2. 实现树形导航交互功能
3. 开发专业详情页基础布局
4. 添加职业路径可视化图表

### 第二阶段（增强功能）
1. 完善搜索和筛选功能
2. 添加信息管理页面
3. 实现页面间的数据传递
4. 优化移动端体验

### 第三阶段（视觉效果）
1. 添加页面切换动画
2. 实现数据加载动画
3. 优化图表交互效果
4. 完善响应式设计

## 数据内容规划

### 预设学科门类（12个）
1. 哲学
2. 经济学  
3. 法学
4. 教育学
5. 文学
6. 历史学
7. 理学
8. 工学
9. 农学
10. 医学
11. 管理学
12. 艺术学

### 数据量级
- 每个门类包含3-5个专业类
- 每个专业类包含3-8个具体专业
- 每个专业关联5-10个相关职业
- 每个职业包含3-5个发展路径级别

## 性能优化策略

1. **图片优化**: 使用WebP格式，实现懒加载
2. **代码分割**: 按页面分割JavaScript代码
3. **缓存策略**: 合理使用浏览器缓存
4. **动画优化**: 使用CSS3硬件加速
5. **数据虚拟化**: 大量数据列表使用虚拟滚动

## 相关文档索引

- [API设计文档](design.md) - 后端API接口设计
- [交互设计文档](interaction.md) - 用户交互设计
- [安装指南](INSTALLATION.md) - 项目安装和部署
- [Windows开发指南](WINDOWS_DEVELOPMENT.md) - Windows环境开发
- [数据库设置说明](DATABASE_SETUP.md) - 数据库初始化
- [项目完成报告](PROJECT_COMPLETION.md) - 项目完成情况

---

**文档版本**: v2.0  
**更新日期**: 2026年1月29日  
**更新说明**: 更新项目结构，反映最新文件组织
