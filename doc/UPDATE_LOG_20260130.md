# 更新日志 - 2026年1月30日

## 问题描述

1. **API 500错误**：访问 `/api/disciplines` 接口时返回500 Internal Server Error
2. **导航树无法渲染**：前端页面 `index.html` 无法正常显示导航树

## 根因分析

### 问题1：ORM对象序列化失败

**错误日志**：
```
Internal Server Error
```

**原因**：在 `main.py` 的 `read_disciplines` 端点中，使用 Pydantic 的 `model_validate()` 方法尝试将包含嵌套关系的 SQLAlchemy ORM 对象序列化为 `DisciplineTree` 模型。

```python
# 原来的代码（有问题）
@app.get("/api/disciplines")
def read_disciplines(...):
    disciplines = crud.get_disciplines(db, ...)
    discipline_trees = [schemas.DisciplineTree.model_validate(d) for d in disciplines]
    return {"code": 200, "message": "success", "data": {"disciplines": discipline_trees}}
```

`DisciplineTree` 模型定义如下（schemas.py）：
```python
class DisciplineTree(Discipline):
    """用于树形导航的学科门类模型，包含专业类和专业列表"""
    major_categories: List[MajorCategoryTree] = Field(default_factory=list)

class MajorCategoryTree(MajorCategory):
    """用于树形导航的专业类模型，包含专业列表"""
    majors: List[MajorTree] = Field(default_factory=list)

class MajorTree(Major):
    """用于树形导航的专业模型"""
    pass
```

**问题**：当 ORM 对象通过 `joinedload()` 加载嵌套关系时，`model_validate()` 无法正确处理这些嵌套的 ORM 对象集合，导致序列化失败。

### 问题2：导航树无数据

由于API 500错误，前端 `main.js` 中的 `disciplines` 变量始终为 `undefined`，导致 `renderMajorTree()` 函数中的 `disciplines.forEach()` 抛出：
```
TypeError: Cannot read properties of undefined (reading 'forEach')
```

## 解决方案

### 解决方案：自定义序列化函数

放弃使用 Pydantic 的 `model_validate()` 序列化嵌套 ORM 对象，改为使用自定义函数手动将 ORM 对象转换为字典。

**修改文件**：`backend/app/main.py`

**新增代码**：
```python
def _discipline_to_tree(discipline):
    """将Discipline ORM对象转换为树形结构字典"""
    if discipline is None:
        return None
    
    result = {
        'id': discipline.id,
        'name': discipline.name,
        'code': discipline.code,
        'description': discipline.description,
        'createdAt': discipline.created_at.isoformat() if discipline.created_at else None,
        'majorCategories': []
    }
    
    # 处理专业类
    if hasattr(discipline, 'major_categories') and discipline.major_categories:
        for category in discipline.major_categories:
            category_dict = {
                'id': category.id,
                'name': category.name,
                'code': category.code,
                'disciplineId': category.discipline_id,
                'description': category.description,
                'createdAt': category.created_at.isoformat() if category.created_at else None,
                'majors': []
            }
            
            # 处理专业
            if hasattr(category, 'majors') and category.majors:
                for major in category.majors:
                    major_dict = {
                        'id': major.id,
                        'name': major.name,
                        'code': major.code,
                        'categoryId': major.category_id,
                        'description': major.description,
                        'duration': major.duration,
                        'mainCourses': [],
                        'createdAt': major.created_at.isoformat() if major.created_at else None
                    }
                    # 处理main_courses（JSON字符串转列表）
                    if major.main_courses:
                        try:
                            if isinstance(major.main_courses, str):
                                major_dict['mainCourses'] = json.loads(major.main_courses)
                            else:
                                major_dict['mainCourses'] = major.main_courses
                        except (json.JSONDecodeError, TypeError):
                            major_dict['mainCourses'] = []
                    category_dict['majors'].append(major_dict)
            
            result['majorCategories'].append(category_dict)
    
    return result
```

**修改API端点**：
```python
@app.get("/api/disciplines")
def read_disciplines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取学科门类列表，包含专业类和专业信息（树形结构）"""
    disciplines = crud.get_disciplines(db, skip=skip, limit=limit)
    # 使用自定义函数将ORM对象转换为字典，处理嵌套关系
    discipline_trees = [_discipline_to_tree(d) for d in disciplines]
    return {"code": 200, "message": "success", "data": {"disciplines": discipline_trees}}
```

## 数据结构

修复后API返回的数据结构符合前端 `main.js` 的期望：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "disciplines": [
      {
        "id": 1,
        "name": "哲学",
        "code": "01",
        "description": "哲学学科门类",
        "createdAt": "2026-01-28T10:21:01.378581",
        "majorCategories": [
          {
            "id": 1,
            "name": "哲学类",
            "code": "0101",
            "disciplineId": 1,
            "description": null,
            "createdAt": "2026-01-28T10:21:01.462965",
            "majors": [
              {
                "id": 1,
                "name": "哲学",
                "code": "010101",
                "categoryId": 1,
                "description": "培养具有系统哲学知识和理论思维能力的人才",
                "duration": 4,
                "mainCourses": ["哲学导论", "逻辑学", "伦理学", "美学", "宗教学"],
                "createdAt": "2026-01-29T04:18:15.574721"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## 数据库状态

| 表名 | 记录数 |
|------|--------|
| disciplines | 4 |
| major_categories | 6 |
| majors | 15 |
| occupations | 0 |

## 已初始化的专业数据

### 哲学 (01)
- 哲学 (010101)
- 逻辑学 (010102)

### 经济学 (02)
- 经济学 (020101)
- 国际经济与贸易(020401)
- 金融学 (020301)
- 保险学 (020303)

### 工学 (08)
- 电子信息工程 (080701)
- 通信工程 (080703)
- 计算机科学与技术 (080901)
- 软件工程 (080902)
- 网络工程 (080903)
- 人工智能 (080717)

### 艺术学 (13)
- 视觉传达设计 (130502)
- 环境设计 (130503)
- 产品设计 (130504)

## 验证步骤

1. **测试API接口**：
   ```bash
   curl http://localhost:8000/api/disciplines
   ```
   预期：返回200状态码和正确的JSON数据

2. **刷新前端页面**：
   - 访问 http://localhost:8001
   - 按 Ctrl+Shift+R 强制刷新
   - 检查导航树是否正确显示

## 注意事项

1. 本次修复采用手动序列化方式，虽然代码稍多，但完全控制序列化过程
2. 确保 `crud.get_disciplines()` 使用 `joinedload()` 正确加载嵌套关系
3. JSON字段（`main_courses`）在序列化时自动从字符串转换为数组
4. 字段名遵循前端约定：使用 camelCase（如 `mainCourses`）而非 snake_case

## 后续优化建议

1. 考虑使用 Pydantic 的 `orm_mode` 或 `from_attributes` 配置简化序列化
2. 考虑使用专门的序列化库如 `sqlalchemy-serializer`
3. 考虑为前端创建专门的 API 响应DTO类

---

**作者**：Matrix Agent  
**日期**：2026年1月30日
