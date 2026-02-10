# 更新日志 - 2026年1月28日

## 概述

本次更新主要解决 SQLite 数据库连接问题，重构了数据库相关代码，并添加了数据库建表脚本。

## 问题描述

1. **数据库连接问题**：前端页面加载时显示空白，数据无法正常显示
2. **路径计算错误**：database.py 中的数据库路径计算存在错误
3. **初始化问题**：后端服务启动时数据库表未能正确创建

## 解决方案

### 1. 重构 database.py

**修改位置**：`backend/app/database.py`

**修改内容**：
- 修复数据库路径计算逻辑
- 添加数据库状态检查函数
- 改进错误处理机制
- 添加详细的状态日志输出

**修改前**：
```python
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
```

**修改后**：
```python
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
DATABASE_DIR = os.path.join(PROJECT_DIR, 'data')
```

### 2. 新增 models.py

**新建文件**：`backend/app/models.py`

将数据模型定义从 database.py 中分离出来，单独存放：
- Discipline（学科门类）
- MajorCategory（专业类）
- Major（专业）
- Occupation（职业）
- MajorOccupation（专业职业关联）
- CareerPath（职业路径）
- PersonalExperience（个人经历）
- ExperienceShare（经验分享）

### 3. 修改 main.py

**修改位置**：`backend/app/main.py`

**修改内容**：
- 改进数据库初始化逻辑
- 添加数据库状态输出
- 使用 init_database() 函数替代直接的 create_tables()

**修改前**：
```python
from .database import get_db, create_tables
create_tables()
```

**修改后**：
```python
from .database import get_db, create_tables, init_database, get_database_file, check_database_exists
db_status = init_database()
print(f"[API] Database initialized: {db_status['database_file']}")
```

### 4. 新增建表脚本

**新建文件**：`setup-database.bat`

提供 Windows 环境下的一键建表功能：
- 自动检查 Python 环境
- 自动创建 data 目录
- 自动安装依赖
- 自动创建数据库表
- 显示数据库状态信息

## 新增文件

| 文件 | 说明 |
|------|------|
| backend/app/models.py | 数据模型定义文件 |
| setup-database.bat | 数据库建表脚本 |
| doc/DATABASE_SETUP.md | 数据库设置说明文档 |
| doc/UPDATE_LOG_20260128.md | 本更新日志 |
| backup/backend_app_20260128/ | 旧版本代码备份 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| backend/app/database.py | 重构 | 改进路径计算和初始化逻辑 |
| backend/app/main.py | 修改 | 改进数据库初始化调用 |
| doc/design.md | 更新 | 添加数据库表结构说明链接 |

## 使用方法

### 方法一：使用建表脚本

双击运行 `setup-database.bat`

### 方法二：启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload
```

服务启动时会自动创建数据库表。

### 方法三：手动建表

```bash
cd backend
pip install -r requirements.txt
python -c "from app.database import create_tables; create_tables()"
```

## 验证步骤

1. **检查数据库文件**：
   - 确认 `data/career_guidance.db` 文件存在
   - 文件大小应大于 0

2. **启动后端服务**：
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
   应看到类似输出：
   ```
   [Database] Database directory: D:\github.com\carrotmet\zyplusv2\data
   [Database] All tables created successfully.
   [Database] Database file: D:\github.com\carrotmet\zyplusv2\data\career_guidance.db
   [API] Database initialized: D:\github.com\carrotmet\zyplusv2\data\career_guidance.db
   ```

3. **初始化示例数据**：
   - 访问 http://localhost:8000/docs
   - 调用 POST /api/init-data 接口

4. **测试 API**：
   - GET /api/disciplines - 获取学科门类
   - GET /api/majors - 获取专业列表
   - GET /api/occupations - 获取职业列表

## 备份说明

旧版本代码已备份到 `backup/backend_app_20260128/` 目录，包括：
- database.py
- main.py
- crud.py
- schemas.py

## 接口兼容性

本次修改不改变任何 API 接口，所有接口保持兼容：
- /api/disciplines
- /api/majors
- /api/occupations
- /api/career-paths
- /api/experiences
- /api/init-data

## 已知问题

1. 如果 data 目录不存在且没有写权限，建表会失败
2. 首次启动后需要手动调用 /api/init-data 初始化示例数据

## 下一步计划

1. 添加数据库迁移工具
2. 添加数据备份功能
3. 优化数据库查询性能
