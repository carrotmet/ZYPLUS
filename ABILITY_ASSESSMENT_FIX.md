# Ability Assessment 保存问题修复记录

## 问题描述
ability_assessment（能力自评）字段无法正确保存，表单提交后恢复默认值。

## 根本原因
1. **浅拷贝问题**：`ProfileFormState.init()` 使用 `{...initialData}` 进行浅拷贝，导致 `ability_assessment` 对象引用相同
2. **对象引用问题**：修改 `currentData.ability_assessment` 时同时影响了 `originalData`
3. **变更检测失败**：`getChanges()` 比较时，两个对象内容相同，无法检测到变化

## 已修复的文件

### 1. profile-form.js

#### 修复 1: 添加深拷贝方法
```javascript
// 深拷贝辅助函数
_deepCopy(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(item => this._deepCopy(item));
    const copy = {};
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            copy[key] = this._deepCopy(obj[key]);
        }
    }
    return copy;
},
```

#### 修复 2: init() 方法使用深拷贝
```javascript
init(userId, initialData = {}) {
    this.userId = userId;
    // 使用深拷贝避免对象引用问题
    this.originalData = this._deepCopy(initialData);
    this.currentData = this._deepCopy(initialData);
},
```

#### 修复 3: reset() 方法使用深拷贝
```javascript
reset() {
    this.currentData = this._deepCopy(this.originalData);
}
```

#### 修复 4: handleSliderGroupChange 创建新对象
```javascript
handleSliderGroupChange(field, subKey, value) {
    const display = document.getElementById(`form-field-${field}-${subKey}-value`);
    if (display) display.textContent = value;
    
    // 创建新对象避免引用问题
    const current = { ...(ProfileFormState.currentData[field] || {}) };
    current[subKey] = parseInt(value);
    ProfileFormState.updateField(field, current);
    
    console.log(`[ProfileForm] ${field}.${subKey} changed to ${value}:`, ProfileFormState.currentData[field]);
},
```

#### 修复 5: 添加调试日志
- `getChanges()` 中添加日志显示变更检测过程
- `submitToAPI()` 中添加日志显示提交数据

### 2. user-profile.html

#### 修复: 添加调试日志
```javascript
function getAbilityAssessment() {
    if (typeof state !== 'undefined' && state.profile && state.profile.ability_assessment) {
        console.log('[getAbilityAssessment] Found:', state.profile.ability_assessment);
        return state.profile.ability_assessment;
    }
    console.log('[getAbilityAssessment] Not found, returning empty object');
    return {};
}
```

## 测试步骤

### 步骤 1: 清除浏览器缓存
按 `Ctrl+Shift+R` 强制刷新页面，确保加载最新的 JS 文件。

### 步骤 2: 打开浏览器控制台
按 `F12` 打开开发者工具，切换到 Console 标签。

### 步骤 3: 打开用户画像表单
1. 在用户画像页面点击"填写"按钮
2. 调整"能力自评"下的滑块（如：逻辑推理从 5 改为 8）
3. 观察控制台输出，应该看到类似：
   ```
   [ProfileForm] ability_assessment.logic changed to 8: {logic: 8, creativity: 5, ...}
   ```

### 步骤 4: 点击保存
1. 点击"保存"按钮
2. 观察控制台输出，检查：
   - `currentData` 是否包含 `ability_assessment`
   - `originalData` 是否与 `currentData` 不同
   - `Changes detected` 是否包含 `ability_assessment`
   - `Submitting to API` 的数据是否正确

### 步骤 5: 验证保存结果
1. 等待保存成功的提示
2. 刷新页面
3. 再次打开表单，检查能力自评滑块是否保持之前的值

## 预期控制台输出

正常情况应该看到：
```
[getAbilityAssessment] Found: {logic: 5, creativity: 5, ...}  // 初始加载
[ProfileForm] ability_assessment.logic changed to 8: {logic: 8, ...}  // 滑块变化
[ProfileFormState] Checking changes...
  currentData: {ability_assessment: {logic: 8, ...}, ...}
  originalData: {ability_assessment: {logic: 5, ...}, ...}
  ability_assessment: changed=true
[ProfileFormState] Changes detected: {ability_assessment: {logic: 8, ...}}
[ProfileForm] Submitting to API: {updates: {ability_assessment: {logic: 8, ...}}}
```

## 如果仍有问题

### 检查 1: 确认文件已更新
在控制台输入：
```javascript
console.log(ProfileFormState._deepCopy);
```
应该输出函数定义，如果不是则缓存未刷新。

### 检查 2: 手动测试深拷贝
```javascript
const test = {a: {b: 1}};
const copy = JSON.parse(JSON.stringify(test));
copy.a.b = 2;
console.log(test.a.b); // 应该是 1
```

### 检查 3: 查看后端数据
```powershell
cd D:\github.com\carrotmet\zyplusv2
python check_db.py
```
检查 `ability_assessment` 字段是否有值。

### 检查 4: 使用测试页面
打开 `tests/test_ability_assessment.html` 文件，测试数据收集逻辑。

## 相关文件
- `profile-form.js` - 表单模块
- `user-profile.html` - 用户画像页面
- `tests/test_ability_assessment.html` - 测试页面
- `backend/app/api_user_profile.py` - 后端 API
