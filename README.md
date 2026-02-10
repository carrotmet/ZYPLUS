# 职业规划导航平台

一个专为高中生和大学生设计的职业规划网站，帮助用户了解专业选择与职业发展的对应关系，打通专业学习与未来职业的信息壁垒。

## 🌟 项目特色

- **专业树形导航**：基于普通高等学校本科专业目录的层级结构
- **职业路径可视化**：清晰的职业发展方向和薪资趋势图表
- **智能推荐系统**：根据专业推荐相关职业，显示匹配度
- **信息管理功能**：用户可添加专业信息，丰富数据库内容
- **响应式设计**：支持桌面端、平板端和移动端访问

## 🎨 设计特色

- **现代简约风格**：采用水鸟色系配色方案，视觉效果清新专业
- **交互动画**：使用Anime.js实现流畅的页面过渡和微交互
- **数据可视化**：ECharts图表展示职业发展和薪资趋势
- **卡片式布局**：清晰的信息层级和充足的留白空间

## 🛠 技术栈

### 前端技术
- **HTML5 + CSS3 + JavaScript ES6+**
- **Tailwind CSS**：快速响应式设计
- **Anime.js**：交互动画库
- **ECharts.js**：数据可视化图表
- **Font Awesome**：统一图标系统

### 部署技术
- **Nginx**：高性能Web服务器
- **Docker**：容器化部署
- **Docker Compose**：多容器编排

## 📁 项目结构

```
career-guidance-website/
├── index.html              # 主页 - 专业选择界面
├── major-detail.html       # 专业详情页 - 职业信息展示
├── add-info.html          # 信息管理页 - 添加专业/职业
├── main.js                # 主要JavaScript逻辑
├── resources/             # 资源文件夹
│   ├── hero-bg.jpg        # 主页背景图
│   ├── career-abstract.jpg # 抽象职业概念图
│   ├── student-avatar1.jpg # 学生头像1
│   └── student-avatar2.jpg # 学生头像2
├── Dockerfile             # Docker镜像构建文件
├── docker-compose.yml     # Docker Compose配置文件
├── nginx.conf            # Nginx服务器配置
├── .dockerignore         # Docker构建忽略文件
├── interaction.md        # 交互设计文档
├── design.md            # 后端API设计文档
├── outline.md           # 项目大纲
└── README.md            # 项目说明文档
```

## 🚀 快速开始

### 本地运行

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd career-guidance-website
   ```

2. **直接运行**
   ```bash
   # 使用Python内置服务器
   python -m http.server 8000
   
   # 或使用Node.js的http-server
   npx http-server -p 8000
   ```

3. **访问网站**
   打开浏览器访问 `http://localhost:8000`

### Docker部署

1. **构建镜像**
   ```bash
   docker build -t career-guidance-website .
   ```

2. **运行容器**
   ```bash
   docker run -d -p 80:80 --name career-guidance-web career-guidance-website
   ```

3. **使用Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 📱 页面功能

### 主页 (index.html)
- **专业树形导航**：左侧显示学科门类、专业类、具体专业的层级结构
- **搜索功能**：实时搜索专业名称和描述
- **专业详情展示**：选中专业后显示详细信息和相关职业
- **热门专业推荐**：展示热门专业卡片

### 专业详情页 (major-detail.html)
- **职业选择**：展示不同职业方向的卡片
- **职业详情**：基本信息、描述、核心要求
- **职业发展路径**：从初级到专家的职业晋升路线
- **薪资趋势图表**：ECharts展示薪资发展情况
- **就业前景分析**：行业需求趋势和技能要求分布

### 信息管理页 (add-info.html)
- **功能切换**：添加专业信息、职业信息或个人经历
- **表单验证**：实时验证输入数据
- **标签输入**：支持课程和要求的标签式输入
- **实时预览**：填写表单时实时显示预览效果
- **最近添加**：显示最近添加的专业、职业和个人经历信息
- **个人经历模块**：用户可分享职业经历和经验
- **新增信息显示**：提交后立即在相应界面显示新增内容

### 经历分享页面 (experience-sharing.html) - 新增
- **经历列表**：以卡片形式展示所有个人经历
- **筛选功能**：按专业、学历、时间等条件筛选
- **搜索功能**：按关键词搜索经历内容
- **经历详情**：点击查看详细个人经历
- **经验分享**：相关经验分享和讨论功能

## 🎯 核心功能

### 专业选择系统
- 基于教育部本科专业目录的完整分类
- 支持树形导航和搜索筛选
- 专业详情包含培养目标、主要课程、学制信息

### 职业路径可视化
- 清晰的职业发展阶段划分
- 每个阶段的薪资水平和工作经验要求
- 交互式图表展示职业发展轨迹

### 数据展示
- 薪资趋势线图
- 行业需求饼图
- 技能要求柱状图
- 响应式图表设计

### 用户交互
- 平滑的页面过渡动画
- 悬停效果和微交互
- 表单验证和错误提示
- 成功操作反馈

## 📊 数据模型

### 专业数据结构
```javascript
{
  id: 80101,
  name: '计算机科学与技术',
  code: '080901',
  discipline: '工学',
  duration: 4,
  description: '专业描述',
  courses: ['数据结构', '计算机网络', '操作系统']
}
```

### 职业数据结构
```javascript
{
  id: 1,
  name: '软件工程师',
  industry: 'IT互联网',
  description: '职业描述',
  requirements: ['编程能力', '算法基础'],
  salaryMin: 12000,
  salaryMax: 50000,
  careerPath: [
    {
      level: '初级',
      title: '初级软件工程师',
      experienceMin: 0,
      experienceMax: 2,
      avgSalary: 15000
    }
  ]
}
```

## 🎨 设计规范

### 配色方案
- **主色调**：#4A90E4 (水鸟蓝)
- **辅助色**：#7BB3F0 (浅蓝)
- **背景色**：#D6E3F8 (极浅蓝)
- **文字色**：#2C3E50 (深灰)

### 字体规范
- **标题字体**：Noto Serif SC (衬线字体)
- **正文字体**：Noto Sans SC (无衬线字体)
- **字体层级**：明确的大小和权重层次

### 组件规范
- **圆角设计**：12px-16px统一圆角
- **阴影效果**：0 4px 20px rgba(74, 144, 228, 0.1)
- **过渡动画**：0.3s ease统一过渡
- **间距系统**：8px基础间距单位

## 🔧 自定义配置

### 修改专业数据
编辑 `main.js` 文件中的 `disciplines` 数组，添加或修改专业信息。

### 修改职业数据
编辑 `major-detail.html` 文件中的 `occupations` 数组，添加或修改职业信息。

### 调整样式
修改各页面中的CSS变量或Tailwind CSS类名来自定义样式。

### 配置Nginx
编辑 `nginx.conf` 文件来自定义服务器配置，如缓存策略、压缩设置等。

## 📈 性能优化

- **图片优化**：使用WebP格式，实现懒加载
- **代码压缩**：HTML、CSS、JavaScript文件压缩
- **缓存策略**：静态资源长期缓存，HTML文件不缓存
- **Gzip压缩**：启用Nginx Gzip压缩
- **CDN加速**：支持静态资源CDN部署

## 🔒 安全特性

- **CSP策略**：内容安全策略防护
- **XSS防护**：XSS攻击防护头
- **点击劫持防护**：X-Frame-Options头
- **内容类型防护**：X-Content-Type-Options头

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 联系方式

- 项目维护者：职业规划导航团队
- 邮箱：contact@career-guidance.com
- 项目地址：[https://github.com/career-guidance/website](https://github.com/career-guidance/website)

## 🙏 致谢

- 感谢所有贡献者的辛勤工作
- 感谢开源社区提供的优秀工具和库
- 感谢用户反馈和建议

---

**职业规划导航平台** - 助力您的职业发展之路