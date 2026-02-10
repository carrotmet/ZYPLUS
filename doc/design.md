# 职业规划网站后端API设计

## 技术栈选择

### 后端框架：FastAPI
- **理由**：现代Python异步框架，性能优秀，自动生成API文档
- **数据库**：SQLite（轻量级，适合demo和快速开发）
- **ORM**：SQLAlchemy（强大的Python ORM工具）
- **数据验证**：Pydantic（类型安全和数据验证）

### 前端框架：Vue 3 + TypeScript
- **UI框架**：Element Plus（成熟的Vue组件库）
- **图表库**：ECharts（数据可视化）
- **动画库**：Anime.js（交互动画）
- **HTTP客户端**：Axios（API请求）

## 数据库设计

### 数据表结构

#### 1. 学科门类表 (disciplines)
```sql
- id: INTEGER PRIMARY KEY
- name: VARCHAR(100) NOT NULL  # 学科名称
- code: VARCHAR(10) NOT NULL   # 学科代码
- description: TEXT            # 学科描述
```

#### 2. 专业类表 (major_categories)
```sql
- id: INTEGER PRIMARY KEY
- name: VARCHAR(100) NOT NULL      # 专业类名称
- code: VARCHAR(10) NOT NULL       # 专业类代码
- discipline_id: INTEGER NOT NULL   # 所属学科ID
- description: TEXT                 # 专业类描述
```

#### 3. 专业表 (majors)
```sql
- id: INTEGER PRIMARY KEY
- name: VARCHAR(100) NOT NULL        # 专业名称
- code: VARCHAR(10) NOT NULL         # 专业代码
- category_id: INTEGER NOT NULL       # 所属专业类ID
- description: TEXT                   # 专业描述
- duration: INTEGER                   # 学制年限
- main_courses: TEXT                  # 主要课程（JSON格式）
- created_at: TIMESTAMP               # 创建时间
```

#### 4. 职业表 (occupations)
```sql
- id: INTEGER PRIMARY KEY
- name: VARCHAR(100) NOT NULL     # 职业名称
- industry: VARCHAR(100)          # 所属行业
- description: TEXT               # 职业描述
- requirements: TEXT              # 要求（JSON格式）
- salary_min: INTEGER             # 最低薪资
- salary_max: INTEGER             # 最高薪资
- created_at: TIMESTAMP           # 创建时间
```

#### 5. 专业职业关联表 (major_occupations)
```sql
- id: INTEGER PRIMARY KEY
- major_id: INTEGER NOT NULL      # 专业ID
- occupation_id: INTEGER NOT NULL  # 职业ID
- match_score: INTEGER            # 匹配度（0-100）
```

#### 6. 职业路径表 (career_paths)
```sql
- id: INTEGER PRIMARY KEY
- occupation_id: INTEGER NOT NULL   # 职业ID
- level: VARCHAR(50) NOT NULL       # 职级（初级、中级、高级等）
- title: VARCHAR(100) NOT NULL      # 职位名称
- experience_min: INTEGER           # 最低经验要求
- experience_max: INTEGER           # 最高经验要求
- avg_salary: INTEGER               # 平均薪资
```

#### 7. 个人经历表 (personal_experiences)
```sql
- id: INTEGER PRIMARY KEY
- nickname: VARCHAR(100) NOT NULL   # 用户昵称
- major_id: INTEGER NOT NULL        # 专业ID
- education: VARCHAR(50) NOT NULL   # 学历（学士/硕士/博士）
- school_name: VARCHAR(200) NOT NULL # 学校名称
- degree: VARCHAR(100)              # 学位名称
- experience: TEXT NOT NULL         # 个人经历详情
- is_anonymous: BOOLEAN DEFAULT FALSE # 是否匿名
- created_at: TIMESTAMP             # 创建时间
- updated_at: TIMESTAMP             # 更新时间
```

#### 8. 经验分享表 (experience_shares)
```sql
- id: INTEGER PRIMARY KEY
- experience_id: INTEGER NOT NULL    # 个人经历ID
- title: VARCHAR(200) NOT NULL       # 分享标题
- content: TEXT NOT NULL             # 分享内容
- tags: TEXT                         # 标签（JSON格式）
- likes: INTEGER DEFAULT 0           # 点赞数
- created_at: TIMESTAMP              # 创建时间
```

## API接口设计

### 1. 学科门类相关接口

#### 获取所有学科门类
```
GET /api/disciplines
Response: {
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "工学",
      "code": "08",
      "description": "工学学科门类",
      "major_categories": [...]  # 包含专业类信息
    }
  ]
}
```

### 2. 专业相关接口

#### 获取专业详情
```
GET /api/majors/{major_id}
Response: {
  "code": 200,
  "data": {
    "id": 1,
    "name": "计算机科学与技术",
    "code": "080901",
    "description": "专业描述",
    "duration": 4,
    "main_courses": ["数据结构", "计算机网络", "操作系统"],
    "related_occupations": [...]  # 相关职业信息
  }
}
```

#### 搜索专业
```
GET /api/majors/search?q={keyword}
Response: 专业列表
```

#### 添加专业
```
POST /api/majors
Body: {
  "name": "专业名称",
  "category_id": 1,
  "description": "专业描述",
  "duration": 4,
  "main_courses": ["课程1", "课程2"]
}
```

### 3. 职业相关接口

#### 获取职业详情
```
GET /api/occupations/{occupation_id}
Response: {
  "code": 200,
  "data": {
    "id": 1,
    "name": "软件工程师",
    "industry": "IT互联网",
    "description": "职业描述",
    "requirements": ["编程能力", "团队协作"],
    "salary_min": 8000,
    "salary_max": 50000,
    "career_paths": [...]  # 职业发展路径
  }
}
```

#### 添加职业
```
POST /api/occupations
Body: {
  "name": "职业名称",
  "industry": "行业",
  "description": "职业描述",
  "requirements": ["要求1", "要求2"],
  "salary_min": 5000,
  "salary_max": 30000
}
```

### 4. 职业路径接口

#### 获取职业发展路径
```
GET /api/career-paths/{occupation_id}
Response: {
  "code": 200,
  "data": [
    {
      "level": "初级",
      "title": "初级软件工程师",
      "experience_min": 0,
      "experience_max": 2,
      "avg_salary": 10000
    },
    {
      "level": "中级", 
      "title": "中级软件工程师",
      "experience_min": 2,
      "experience_max": 5,
      "avg_salary": 20000
    }
  ]
}
```

### 5. 推荐系统接口

#### 获取专业推荐职业
```
GET /api/recommendations/majors/{major_id}/occupations
Response: {
  "code": 200,
  "data": [
    {
      "occupation": {...},
      "match_score": 95
    }
  ]
}
```

### 6. 个人经历接口

#### 添加个人经历
```
POST /api/experiences
Body: {
  "nickname": "用户昵称",
  "major_id": 1,
  "education": "学士",
  "school_name": "清华大学",
  "degree": "计算机科学与技术学士",
  "experience": "详细的工作经历...",
  "is_anonymous": false
}
Response: {
  "code": 200,
  "data": {
    "id": 1,
    "nickname": "用户昵称",
    "major_name": "计算机科学与技术",
    "education": "学士",
    "school_name": "清华大学",
    "experience": "详细的工作经历...",
    "created_at": "2024-10-23T10:00:00Z"
  }
}
```

#### 获取个人经历列表
```
GET /api/experiences?page=1&limit=10
Response: {
  "code": 200,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "limit": 10
  }
}
```

#### 获取专业相关经历
```
GET /api/experiences/major/{major_id}
Response: {
  "code": 200,
  "data": [
    {
      "id": 1,
      "nickname": "用户昵称",
      "education": "学士",
      "school_name": "清华大学",
      "experience": "详细的工作经历...",
      "created_at": "2024-10-23T10:00:00Z"
    }
  ]
}
```

### 7. 经验分享接口

#### 添加经验分享
```
POST /api/experiences/{experience_id}/shares
Body: {
  "title": "软件工程师职业发展建议",
  "content": "详细的内容...",
  "tags": ["职业规划", "技术成长"]
}
```

#### 获取经验分享列表
```
GET /api/experiences/{experience_id}/shares
Response: {
  "code": 200,
  "data": [
    {
      "id": 1,
      "title": "软件工程师职业发展建议",
      "content": "详细的内容...",
      "tags": ["职业规划", "技术成长"],
      "likes": 15,
      "created_at": "2024-10-23T10:00:00Z"
    }
  ]
}
```

### 8. 新增信息显示接口（本次开发重点）

#### 获取最新添加的专业
```
GET /api/majors/latest?limit=5
Response: {
  "code": 200,
  "data": {
    "majors": [...],
    "total": 5
  }
}
```

#### 获取最新添加的职业
```
GET /api/occupations/latest?limit=5
Response: {
  "code": 200,
  "data": {
    "occupations": [...],
    "total": 5
  }
}
```

#### 获取最新添加的个人经历
```
GET /api/experiences/latest?limit=5
Response: {
  "code": 200,
  "data": {
    "experiences": [...],
    "total": 5
  }
}
```

#### 实时数据同步WebSocket（预留）
```
WS /api/ws/updates
Message: {
  "type": "new_major",
  "data": {
    "id": 1,
    "name": "新专业名称",
    "category_id": 1
  }
}
```

## 前端组件架构

### 主要页面组件

1. **HomePage.vue** - 主页专业选择器
2. **MajorDetailPage.vue** - 专业详情页
3. **OccupationDetailPage.vue** - 职业详情页  
4. **AddInfoPage.vue** - 添加信息页

### 可复用组件

1. **MajorTree.vue** - 专业树形导航
2. **OccupationCard.vue** - 职业信息卡片
3. **CareerPathChart.vue** - 职业路径图表
4. **SalaryChart.vue** - 薪资趋势图表
5. **SearchBox.vue** - 搜索框组件

## Docker配置

### Dockerfile

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY .. .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```