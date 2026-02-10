# 文件重组记录 - 2024年2月8日

> 本次重组将散落的测试文件统一放置到 `tests/` 目录，并新增AI隐式调用测试文件。

---

## 一、文件移动记录

### 1. 测试文件迁移

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `test_api.py` | `tests/test_api.py` | API测试脚本 |
| `test_dspy_intent.py` | `tests/test_dspy_intent.py` | DSPy意图测试 |
| `test_dspy_simple.py` | `tests/test_dspy_simple.py` | DSPy简单测试 |

### 2. 新增测试文件

| 文件路径 | 说明 |
|----------|------|
| `tests/test_ai_profile_update.py` | AI隐式调用表单更新的后端测试 |
| `tests/test_ai_profile_update.js` | AI隐式调用表单更新的前端测试代码 |

---

## 二、目录结构变化

### 重组前
```
D:\github.com\carrotmet\zyplusv2\
├── test_api.py                 # 散落的测试文件
├── test_dspy_intent.py         # 散落的测试文件
├── test_dspy_simple.py         # 散落的测试文件
├── check_db.py                 # 数据库检查工具（保留根目录）
├── verify_module.py            # 模块验证工具（保留根目录）
├── ...
```

### 重组后
```
D:\github.com\carrotmet\zyplusv2\
├── tests/                      # 测试文件统一目录
│   ├── test_api.py             # API测试
│   ├── test_dspy_intent.py     # DSPy意图测试
│   ├── test_dspy_simple.py     # DSPy简单测试
│   ├── test_ai_profile_update.py   # AI隐式调用后端测试（新增）
│   └── test_ai_profile_update.js   # AI隐式调用前端测试（新增）
├── check_db.py                 # 数据库检查工具（保留）
├── verify_module.py            # 模块验证工具（保留）
├── ...
```

---

## 三、未移动的文件

以下文件保留在原位置，因为它们不是测试文件或具有特殊用途：

| 文件路径 | 保留原因 |
|----------|----------|
| `check_db.py` | 数据库检查工具，开发常用，保留根目录方便调用 |
| `verify_module.py` | 模块验证工具，用于环境检查 |

---

## 四、AI隐式调用测试说明

### 测试内容

新增的两个测试文件用于测试 **AI隐式调用表单更新** 功能：

1. **`tests/test_ai_profile_update.py`** - 后端API测试
   - 测试 `/api/user-profiles/{user_id}/ai-update` 接口
   - 测试RAG服务集成AI更新的完整流程
   - 使用方法：`python tests\test_ai_profile_update.py`

2. **`tests/test_ai_profile_update.js`** - 前端测试代码
   - 提供浏览器控制台可执行的测试函数
   - 包含4个测试场景：基础AI更新、RAG流程、批量更新、方式对比
   - 使用方法：在浏览器控制台粘贴代码后执行测试函数

### AI隐式调用流程

```
用户对话
    ↓
RAG服务处理（intent识别 + 信息提取）
    ↓
提取结构化数据（career_path_preference, value_priorities等）
    ↓
调用 ProfileForm.updateByAI() 或后端 /ai-update API
    ↓
更新数据库（user_profiles表）
    ↓
记录更新日志（user_profile_logs表）
    ↓
刷新前端UI（updateUIFromProfileData）
    ↓
显示更新通知（静默或显式）
```

### 手动表单 vs AI隐式调用对比

| 特性 | 手动表单 | AI隐式调用 |
|------|----------|-----------|
| 触发方式 | 用户点击"填写"按钮 | AI自动检测并调用 |
| 用户可见性 | 弹出表单，用户可编辑 | 静默执行，无弹窗 |
| API端点 | `/form-update` | `/ai-update` |
| 前端调用 | `ProfileForm.open()` | `ProfileForm.updateByAI()` |
| 适用场景 | 用户主动完善信息 | AI从对话中自动提取 |

---

## 五、使用指南

### 运行后端测试

```powershell
cd D:\github.com\carrotmet\zyplusv2
python tests\test_ai_profile_update.py
```

### 运行前端测试

1. 打开浏览器，进入用户画像页面
2. 按 F12 打开控制台
3. 复制 `tests/test_ai_profile_update.js` 的内容粘贴到控制台
4. 执行测试函数，如：`testAIProfileUpdate()`

### 查看所有测试文件

```powershell
ls tests\*.py
ls tests\*.js
```

---

## 六、注意事项

1. **业务代码未移动**：仅移动了测试文件，所有业务相关代码（`backend/`, `frontend/`, `user-profile.js` 等）保持在原位置

2. **路径引用检查**：移动后检查现有代码中是否有硬编码的测试文件路径引用

3. **导入路径**：测试文件中的导入路径已使用相对路径或动态添加 `sys.path`，确保能正确导入 backend 模块

---

## 七、后续建议

1. 考虑将 `check_db.py` 和 `verify_module.py` 也移入 `tests/` 或新建 `tools/` 目录
2. 为测试目录添加 `__init__.py` 使其成为Python包
3. 添加 `tests/README.md` 说明各个测试文件的用途

---

记录人：AI Assistant  
日期：2026-02-08
