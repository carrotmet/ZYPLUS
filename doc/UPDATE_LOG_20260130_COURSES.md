# 更新日志 - 2026年1月30日（课程信息渲染问题）

## 问题描述

1. **导航树无法显示课程详情**：点击导航树的子目录（如"哲学-哲学类-逻辑学"）时，具体课程信息未能正确渲染
2. **浏览器控制台报错**：
   ```
   main.js:410  Uncaught TypeError: Cannot read properties of undefined (reading 'forEach')
       at renderMajorDetails (main.js:410:19)
       at selectMajor (main.js:381:5)
   ```

## 根因分析

### 字段名不匹配

**错误代码位置**（main.js 第468-475行）：
```javascript
// 渲染课程
const coursesContainer = detailsElement.querySelector('#majorCourses');
major.courses.forEach(course => {  // ← 问题所在
    const courseTag = document.createElement('span');
    courseTag.className = 'bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm';
    courseTag.textContent = course;
    coursesContainer.appendChild(courseTag);
});
```

**问题分析**：
- 前端 `renderMajorDetails` 函数使用 `major.courses` 获取课程列表
- 后端API返回的专业数据中，课程字段名为 `mainCourses`（驼峰命名）
- 当调用 `major.courses.forEach()` 时，由于 `major.courses` 为 `undefined`
- JavaScript 抛出 `TypeError: Cannot read properties of undefined (reading 'forEach')`

**后端API返回的数据结构**：
```json
{
  "id": 1,
  "name": "哲学",
  "code": "010101",
  "mainCourses": ["哲学导论", "逻辑学", "伦理学", "美学", "宗教学"],
  ...
}
```

## 解决方案

### 修改文件：`main.js`

**修改位置**：第468-475行的 `renderMajorDetails` 函数

**修改前**：
```javascript
// 渲染课程
const coursesContainer = detailsElement.querySelector('#majorCourses');
major.courses.forEach(course => {
    const courseTag = document.createElement('span');
    courseTag.className = 'bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm';
    courseTag.textContent = course;
    coursesContainer.appendChild(courseTag);
});
```

**修改后**：
```javascript
// 渲染课程
const coursesContainer = detailsElement.querySelector('#majorCourses');
const courses = major.mainCourses || [];
courses.forEach(course => {
    const courseTag = document.createElement('span');
    courseTag.className = 'bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm';
    courseTag.textContent = course;
    coursesContainer.appendChild(courseTag);
});
```

### 修改说明

1. **字段名修正**：`major.courses` → `major.mainCourses`
   - 与后端API返回的字段名保持一致

2. **添加空值检查**：`major.mainCourses || []`
   - 如果 `mainCourses` 字段不存在或为 null，使用空数组作为默认值
   - 防止 `forEach` 调用时的类型错误

3. **中间变量**：引入 `const courses = ...`
   - 提高代码可读性
   - 方便调试

## 验证步骤

1. **刷新前端页面**：
   - 访问 http://localhost:8001
   - 按 **Ctrl+Shift+R** 强制刷新

2. **测试课程显示**：
   - 点击导航树中的任意专业（如"哲学 > 哲学类 > 逻辑学"）
   - 确认右侧详情区域正确显示课程标签

3. **验证课程数据**：

   | 专业名称 | 预期课程数量 | 课程列表 |
   |---------|-------------|---------|
   | 哲学 | 5门 | 哲学导论、逻辑学、伦理学、美学、宗教学 |
   | 逻辑学 | 5门 | 数理哲学、逻辑学导论、计算逻辑、语言逻辑、认识逻辑 |
   | 经济学 | 4门 | 微观经济学、宏观经济学、计量经济学、国际经济学 |
   | 计算机科学与技术 | 5门 | 数据结构、计算机网络、操作系统、数据库原理、软件工程 |

## 相关文件修改

| 文件 | 修改内容 |
|------|---------|
| `main.js` | `renderMajorDetails` 函数中修正字段名并添加空值检查 |

## 总结

本次问题是由前端代码与后端API字段命名不一致导致的数据读取失败。通过以下两步修复：

1. 将 `major.courses` 改为 `major.mainCourses`（与后端一致）
2. 添加空值检查 `|| []`（防止 undefined 导致报错）

---

**作者**：Matrix Agent  
**日期**：2026年1月30日
