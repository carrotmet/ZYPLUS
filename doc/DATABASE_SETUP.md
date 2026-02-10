# 数据库建表与初始化说明

## 概述

本文档说明如何为职业规划导航平台创建和初始化 SQLite 数据库。

## 数据库位置

数据库文件存储在项目根目录下的 `data` 文件夹中：
- 完整路径：`项目目录/data/career_guidance.db`
- 数据库类型：SQLite
- 表数量：8个数据表

## 快速开始

### 方法一：使用建表脚本（推荐）

双击运行项目根目录下的 `setup-database.bat` 脚本，脚本会自动完成所有设置。

### 方法二：手动建表

```bash
cd backend
pip install -r requirements.txt
python -c "from app.database import create_tables; create_tables()"
```

### 方法三：使用后端服务自动建表

启动后端服务时，数据库会自动初始化：
```bash
cd backend
python -m uvicorn app.main:app --reload
```

## 数据库表结构

### 1. disciplines（学科门类表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 学科名称 |
| code | VARCHAR(10) | 学科代码（唯一） |
| description | TEXT | 学科描述 |
| created_at | TIMESTAMP | 创建时间 |

### 2. major_categories（专业类表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 专业类名称 |
| code | VARCHAR(10) | 专业类代码 |
| discipline_id | INTEGER | 所属学科ID（外键） |
| description | TEXT | 专业类描述 |
| created_at | TIMESTAMP | 创建时间 |

### 3. majors（专业表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 专业名称 |
| code | VARCHAR(10) | 专业代码（唯一） |
| category_id | INTEGER | 所属专业类ID（外键） |
| description | TEXT | 专业描述 |
| duration | INTEGER | 学制年限 |
| main_courses | TEXT | 主要课程（JSON格式） |
| created_at | TIMESTAMP | 创建时间 |

### 4. occupations（职业表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 职业名称 |
| industry | VARCHAR(100) | 所属行业 |
| description | TEXT | 职业描述 |
| requirements | TEXT | 要求（JSON格式） |
| salary_min | INTEGER | 最低薪资 |
| salary_max | INTEGER | 最高薪资 |
| created_at | TIMESTAMP | 创建时间 |

### 5. major_occupations（专业职业关联表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| major_id | INTEGER | 专业ID（外键） |
| occupation_id | INTEGER | 职业ID（外键） |
| match_score | INTEGER | 匹配度（0-100） |

### 6. career_paths（职业路径表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| occupation_id | INTEGER | 职业ID（外键） |
| level | VARCHAR(50) | 职级 |
| title | VARCHAR(100) | 职位名称 |
| experience_min | INTEGER | 最低经验要求 |
| experience_max | INTEGER | 最高经验要求 |
| avg_salary | INTEGER | 平均薪资 |

### 7. personal_experiences（个人经历表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| nickname | VARCHAR(100) | 用户昵称 |
| major_id | INTEGER | 专业ID（外键） |
| education | VARCHAR(50) | 学历 |
| school_name | VARCHAR(200) | 学校名称 |
| degree | VARCHAR(100) | 学位名称 |
| experience | TEXT | 个人经历详情 |
| is_anonymous | BOOLEAN | 是否匿名 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 8. experience_shares（经验分享表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| experience_id | INTEGER | 个人经历ID（外键） |
| title | VARCHAR(200) | 分享标题 |
| content | TEXT | 分享内容 |
| tags | TEXT | 标签（JSON格式） |
| likes | INTEGER | 点赞数 |
| created_at | TIMESTAMP | 创建时间 |

## 初始化示例数据

启动服务后，通过 API 初始化示例数据：
- API 端点：POST /api/init-data
- API 文档：http://localhost:8000/docs

初始化数据包括：
- 4个学科门类（哲学、经济学、工学、艺术学）
- 6个专业类
- 7个专业
- 3个职业
- 若干职业路径

## 故障排除

### 问题1：无法创建data目录
检查项目目录的写权限，或手动创建data目录。

### 问题2：数据库连接失败
确保没有其他程序正在使用数据库文件。

### 问题3：表创建失败
检查 Python 依赖是否安装：pip install -r requirements.txt

### 问题4：数据查询返回空
首次启动后需要调用 /api/init-data 初始化示例数据。

## 相关文件

| 文件 | 说明 |
|------|------|
| backend/app/database.py | 数据库连接和初始化 |
| backend/app/models.py | 数据模型定义 |
| backend/app/crud.py | 数据操作函数 |
| backend/app/schemas.py | Pydantic 数据验证 |
| setup-database.bat | 数据库建表脚本 |
| data/career_guidance.db | SQLite 数据库文件 |
