# 测试文件目录

> 所有测试文件统一存放于此目录

---

## 测试文件清单

### Python 后端测试

| 文件 | 用途 | 运行方式 |
|------|------|----------|
| `test_api.py` | API接口测试 | `python tests\test_api.py` |
| `test_dspy_intent.py` | DSPy意图识别测试 | `python tests\test_dspy_intent.py` |
| `test_dspy_simple.py` | DSPy简单测试 | `python tests\test_dspy_simple.py` |
| `test_ai_profile_update.py` | AI隐式调用表单更新测试 | `python tests\test_ai_profile_update.py` |

### JavaScript 前端测试

| 文件 | 用途 | 运行方式 |
|------|------|----------|
| `test_ai_profile_update.js` | AI隐式调用前端测试 | 浏览器控制台粘贴执行 |

---

## AI隐式调用表单更新 - 测试指南

### 什么是AI隐式调用？

AI隐式调用是指：**AI在对话过程中自动识别并提取用户画像信息，无需用户手动填写表单，直接更新数据库**。

与手动表单的区别：
- **手动表单**：用户点击"填写"按钮 → 弹出表单 → 用户输入 → 保存
- **AI隐式调用**：用户对话 → AI提取信息 → 自动保存（无感知）

### 测试流程

#### 方法一：后端API测试（推荐）

```powershell
cd D:\github.com\carrotmet\zyplusv2
python tests\test_ai_profile_update.py
```

**测试内容：**
1. 创建测试用户画像
2. 模拟AI提取结构化数据
3. 调用 `/ai-update` API更新画像
4. 验证数据库更新和日志记录

#### 方法二：前端浏览器测试

**步骤：**
1. 打开浏览器，进入用户画像页面 (`user-profile.html`)
2. 按 F12 打开开发者工具 → Console
3. 复制 `tests/test_ai_profile_update.js` 的全部内容
4. 粘贴到控制台并回车
5. 执行测试函数：
   ```javascript
   testAIProfileUpdate()      // 基础AI更新测试
   testRAGFlowWithAIUpdate()  // RAG完整流程测试
   testBatchAIUpdate()        // 批量更新测试
   compareUpdateMethods()     // 对比更新方式
   ```

**预期结果：**
- 控制台显示更新成功
- 页面右侧画像模块自动刷新
- 显示AI更新通知（绿色提示）

#### 方法三：手动集成测试

在RAG服务中集成AI隐式调用：

```python
# backend/app/services/rag_service.py

def process_message(self, user_message, user_profile, ...):
    # 1. 提取信息
    extracted = self._extract_information(user_message, intent)
    
    # 2. 如果有提取到画像字段，调用AI更新
    if extracted:
        # 这里可以调用API或直接更新数据库
        requests.post(
            f"http://localhost:8000/api/user-profiles/{user_id}/ai-update",
            json={
                "updates": extracted,
                "reason": "从对话中提取",
                "source": "ai_extraction"
            }
        )
    
    return {"reply": "...", "extracted_info": extracted}
```

### AI隐式调用完整流程

```
用户: "我喜欢编程，想走技术路线"
    ↓
RAG服务:
  ├─ 意图识别: career_advice
  ├─ 信息提取: 
  │   ├─ career_path_preference = "technical"
  │   └─ interests = ["编程"]
  └─ 生成回复: "技术路线很适合你..."
    ↓
AI隐式更新:
  ├─ 调用 ProfileForm.updateByAI()
  ├─ POST /api/user-profiles/{user_id}/ai-update
  ├─ 更新 user_profiles 表
  └─ 记录 user_profile_logs 日志
    ↓
前端响应:
  ├─ 返回更新后的画像数据
  ├─ 调用 updateUIFromProfileData()
  ├─ 刷新右侧画像模块显示
  └─ 显示通知: "AI已自动记录: 职业路径偏好"
    ↓
用户看到:
  - AI回复了对话
  - 右侧"职业路径偏好"从"未设置"变为"技术专家路径"
  - 完整度从0%上升到10%
  - 右上角显示更新提示
```

### 关键API端点

#### 1. AI隐式更新（AI自动调用）
```
POST /api/user-profiles/{user_id}/ai-update
Content-Type: application/json

{
    "updates": {
        "career_path_preference": "technical",
        "value_priorities": ["成就感", "创新"]
    },
    "reason": "从对话中提取",
    "source": "ai_extraction"
}
```

#### 2. 手动表单更新（用户主动填写）
```
POST /api/user-profiles/{user_id}/form-update
Content-Type: application/json

{
    "updates": {
        "holland_code": "RIA",
        "mbti_type": "INTJ"
    }
}
```

### 前端调用方式

#### AI隐式调用（JavaScript）
```javascript
// 方式1: 使用 ProfileForm 模块（推荐）
await ProfileForm.updateByAI(userId, {
    career_path_preference: 'technical',
    value_priorities: ['成就感', '创新']
}, '从对话中提取');

// 方式2: 直接调用API
await fetch(`http://localhost:8000/api/user-profiles/${userId}/ai-update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        updates: { career_path_preference: 'technical' },
        reason: 'AI提取'
    })
});
```

### 常见问题

**Q: AI隐式调用和手动表单的数据会冲突吗？**  
A: 不会。两者更新的是同一个数据库表，后更新的会覆盖先更新的字段。

**Q: 如何知道AI是否正确提取了信息？**  
A: 
1. 查看浏览器控制台日志
2. 查看数据库 `user_profile_logs` 表
3. 观察页面右侧画像模块是否自动刷新

**Q: AI提取的信息不准确怎么办？**  
A: 用户可以点击"填写"按钮，手动修改AI更新的字段。

---

## 其他测试

### API测试
```powershell
python tests\test_api.py
```

### DSPy测试（需要配置API Key）
```powershell
python tests\test_dspy_intent.py
python tests\test_dspy_simple.py
```

---

## 注意事项

1. **运行测试前确保后端服务已启动** (`http://localhost:8000`)
2. **前端测试需要在用户画像页面执行**
3. **测试会创建临时用户数据，测试完成后可手动清理**
