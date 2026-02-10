# 职业规划导航平台 - 安装指南

## 🚀 快速安装

### 前提条件
- Docker 和 Docker Compose 已安装
- Python 3.9+（用于测试）
- Git（用于克隆项目）

### 方法一：使用启动脚本（推荐）

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd career-guidance-website
   ```

2. **运行启动脚本**
   ```bash
   ./start.sh
   ```

3. **访问应用**
   - 前端地址: http://localhost
   - API文档: http://localhost:8000/docs

### 方法二：手动安装

1. **启动后端服务**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **启动前端服务（新终端）**
   ```bash
   # 使用Python内置服务器
   python -m http.server 8001
   
   # 或使用Node.js的http-server
   npx http-server -p 8001
   ```

3. **访问应用**
   - 前端地址: http://localhost:8001
   - API文档: http://localhost:8000/docs

### 方法三：使用Docker Compose

1. **构建和启动**
   ```bash
   docker-compose up -d
   ```

2. **查看日志**
   ```bash
   docker-compose logs -f
   ```

3. **停止服务**
   ```bash
   docker-compose down
   ```

## 🧪 测试应用

### 测试API接口
```bash
python test-api.py
```

### 手动测试
1. 访问 http://localhost:8000/docs 查看API文档
2. 使用Swagger UI测试各个接口
3. 访问前端页面测试交互功能

## 📋 常用命令

### Docker Compose命令
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 重新构建
docker-compose build
```

### 后端开发命令
```bash
# 安装依赖
cd backend && pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload

# 初始化数据库
python -c "from backend.app.database import create_tables; create_tables()"
```

### 前端开发命令
```bash
# 启动开发服务器
python -m http.server 8001

# 或使用live-server
live-server --port=8001
```

## 🔧 配置说明

### 环境变量
创建 `.env` 文件：
```env
# 数据库配置
DATABASE_URL=sqlite:///app/data/career_guidance.db

# 应用配置
DEBUG=True
SECRET_KEY=your-secret-key-here

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

### 数据库配置
- 默认使用SQLite数据库
- 数据文件位置: `./data/career_guidance.db`
- 自动创建表结构

### Nginx配置
- 配置文件: `nginx.conf`
- 默认端口: 80
- 支持静态文件服务和API代理

## 📊 项目结构

```
career-guidance-website/
├── backend/                    # 后端代码
│   ├── app/                   # FastAPI应用
│   │   ├── main.py           # 主应用文件
│   │   ├── database.py       # 数据库模型
│   │   ├── schemas.py        # 数据验证
│   │   └── crud.py          # 数据库操作
│   ├── requirements.txt      # Python依赖
│   └── Dockerfile           # 后端镜像
├── frontend/                  # 前端文件
│   ├── index.html           # 主页
│   ├── major-detail.html    # 职业详情页
│   ├── add-info.html       # 信息管理页
│   ├── main.js             # 主要逻辑
│   ├── add-info.js        # 信息管理逻辑
│   ├── api-service.js    # API服务
│   └── resources/        # 资源文件
├── data/                   # 数据目录
├── logs/                  # 日志目录
├── docker-compose.yml    # 容器编排
├── Dockerfile           # 前端镜像
├── nginx.conf          # Nginx配置
├── start.sh           # 启动脚本
└── test-api.py       # API测试脚本
```

## 🎯 功能验证

### 核心功能检查清单
- [ ] 专业树形导航正常显示
- [ ] 搜索功能正常工作
- [ ] 专业详情页面正常加载
- [ ] 职业详情页面正常加载
- [ ] 图表正常渲染
- [ ] 表单可以正常提交
- [ ] 个人经历功能正常工作
- [ ] API接口正常响应

### 新增功能验证（个人经历模块）
- [ ] 个人经历表单显示正常
- [ ] 表单验证功能正常
- [ ] 实时预览功能正常
- [ ] 提交功能正常
- [ ] 数据存储正常

### 新增信息显示功能验证
- [ ] 新增专业信息立即显示在主页
- [ ] 新增职业信息立即显示在职业详情页
- [ ] 新增个人经历立即显示在经历分享页
- [ ] 数据同步正常，无需刷新页面
- [ ] 经历分享页面正常加载和显示

## 🔍 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口使用情况
   lsof -i :8000
   lsof -i :80
   
   # 修改端口配置
   # 编辑 docker-compose.yml 或后端配置文件
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库文件权限
   ls -la data/
   
   # 重新初始化数据库
   python -c "from backend.app.database import create_tables; create_tables()"
   ```

3. **前端无法连接后端**
   ```bash
   # 检查API服务状态
   curl http://localhost:8000/
   
   # 检查CORS配置
   # 查看 backend/app/main.py 中的 CORS 设置
   ```

4. **Docker镜像构建失败**
   ```bash
   # 清理缓存
   docker system prune -a
   
   # 重新构建
   docker-compose build --no-cache
   ```

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看后端详细日志
docker-compose exec backend tail -f /var/log/uvicorn.log
```

## 📈 性能优化

### 前端优化
- 启用Gzip压缩
- 图片懒加载
- CSS和JS文件压缩
- 缓存策略配置

### 后端优化
- 数据库索引优化
- 查询性能优化
- 连接池配置
- 缓存机制

## 🔒 安全配置

### 生产环境配置
1. 使用HTTPS
2. 配置防火墙
3. 设置访问控制
4. 定期备份数据
5. 监控安全日志

### 环境安全
- 修改默认密码
- 限制API访问频率
- 验证输入数据
- 防止SQL注入

## 📚 文档资源

- [项目说明](../README.md) - 项目概述和使用说明
- [交互设计](interaction.md) - 用户交互设计文档
- [API设计](design.md) - 后端API设计文档
- [项目大纲](outline.md) - 项目结构和功能规划
- [完成报告](PROJECT_COMPLETION.md) - 项目完成详细报告

## 🤝 贡献指南

1. **报告问题**: 提交Issue描述问题
2. **功能建议**: 提交Issue提出建议
3. **代码贡献**: Fork项目并提交Pull Request
4. **文档完善**: 帮助完善项目文档

## 📞 技术支持

如有问题，请检查：
1. 项目文档
2. API文档: http://localhost:8000/docs
3. 日志信息
4. 常见问题解答

---

**职业规划导航平台** - 助力您的职业发展之路