# Windows 环境开发指南

## 概述

本文档介绍如何在 Windows 系统下搭建和运行职业规划导航平台的开发环境。通过本指南，开发人员可以在 Windows 操作系统上进行后端 API 接口的调试和前端页面的开发工作。

本项目采用前后端分离架构，后端基于 FastAPI 框架构建，提供 RESTful API 服务；前端使用原生 HTML、CSS 和 JavaScript 构建，提供用户界面。Windows 环境开发支持包括独立启动后端服务、独立启动前端服务、一键启动完整开发环境以及 API 接口测试等功能。

## 环境准备

### 必要软件安装

在开始开发之前，需要确保 Windows 系统已安装以下软件。这些软件是进行 Python 后端开发和前端服务运行的基础环境。

**Python 3.9 或更高版本**是运行本项目后端服务的必要环境。推荐从 Python 官方网站下载最新版本的 Python 安装包。安装过程中请务必勾选「Add Python to PATH」选项，这将自动配置环境变量，使你可以在命令行中直接使用 python 命令。安装完成后，可以通过在命令提示符中执行 `python --version` 来验证安装是否成功。如果看到类似 `Python 3.11.5` 的版本号输出，说明 Python 环境已正确配置。

**Git（可选）**用于版本控制和代码管理。如果你需要从远程仓库克隆代码或参与团队协作开发，需要安装 Git for Windows。安装完成后，可以在命令提示符中使用 git 命令进行版本控制操作。即使不参与协作开发，Git 仍然是一个值得安装的工具，它可以方便地管理项目代码的历史版本。

### 可选软件安装

以下软件虽然不是必需，但可以显著提升开发效率和体验。建议根据个人习惯选择性安装。

**VS Code**是一个轻量级但功能强大的代码编辑器，对 JavaScript 和 Python 开发有良好的支持。通过安装相关扩展，可以获得代码智能提示、语法高亮、调试支持等功能，大幅提升开发效率。VS Code 的终端功能可以直接在编辑器内调用 Windows 命令提示符，方便执行各种开发命令。

**Postman**是一个专业的 API 测试工具。虽然项目提供了 test-api.py 测试脚本，但 Postman 提供了更直观的图形界面，可以更灵活地构建和发送 HTTP 请求，查看响应结果，非常适合进行接口调试和探索性测试。

**Node.js（可选）**如果需要使用 npx http-server 等工具启动前端服务，需要安装 Node.js。对于大多数开发场景，Python 内置的 HTTP 服务器已经足够使用，安装 Node.js 是可选的。

## 快速启动

### 方法一：一键启动（推荐）

项目提供了一键启动脚本，可以同时启动后端服务和前端服务，快速搭建完整的开发环境。

双击运行项目根目录下的 `start-dev.bat` 文件，或者在命令提示符中执行该脚本。脚本启动后会显示菜单选项，输入数字 `1` 并回车，即可启动完整的开发环境。脚本会自动检查 Python 环境、安装后端依赖、创建必要目录，并分别启动后端服务（端口 8000）和前端服务（端口 8001）。

启动成功后，会看到两个新的命令提示符窗口分别运行后端服务和前端服务。主窗口会显示访问地址信息，包括前端地址 http://localhost:8001、后端 API 地址 http://localhost:8000 以及 API 文档地址 http://localhost:8000/docs。此时，打开浏览器访问 http://localhost:8001 即可查看前端页面，访问 http://localhost:8000/docs 可以查看和测试 API 接口。

### 方法二：独立启动服务

如果只需要启动特定服务，可以使用独立的启动脚本。

**启动后端服务**：双击运行 `start-backend.bat` 文件，或者在命令提示符中执行该脚本。后端服务将在 http://localhost:8000 上启动，提供 API 服务。服务启动后会自动初始化 SQLite 数据库（如数据目录不存在）。可以通过访问 http://localhost:8000/docs 查看 Swagger API 文档。

**启动前端服务**：双击运行 `start-frontend.bat` 文件，或者在命令提示符中执行该脚本。前端服务将在 http://localhost:8001 上启动，提供静态文件服务。此脚本使用 Python 内置的 HTTP 服务器，不需要额外安装依赖。

### 方法三：手动启动

如果你需要更精细的控制，也可以手动执行启动命令。

首先打开命令提示符，切换到项目目录。然后执行以下命令启动后端服务：

```cmd
cd D:\github.com\carrotmet\zyplusv2\backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

接着打开另一个命令提示符窗口，启动前端服务：

```cmd
cd D:\github.com\carrotmet\zyplusv2
python -m http.server 8001
```

手动启动方式适合需要调试服务启动过程或自定义启动参数的场景。

## 服务说明

### 后端服务

后端服务基于 FastAPI 框架构建，运行在 Windows PowerShell 或命令提示符环境中。服务默认监听 8000 端口，提供完整的 RESTful API 接口。启动时服务会自动检查并初始化 SQLite 数据库，在项目根目录的 data 目录下创建 career_guidance.db 数据库文件。

服务启动后会显示以下信息：服务地址 http://localhost:8000、API 文档地址 http://localhost:8000/docs，以及 OpenAPI 规范地址 http://localhost:8000/openapi.json。FastAPI 自动生成的 Swagger UI 文档提供了直观的接口测试界面，可以直接在浏览器中测试各个 API 接口。

开发过程中对后端代码的修改会自动加载（得益于 --reload 参数），无需重启服务即可看到代码变更效果。这大大提升了开发效率，开发者可以专注于代码编写和调试。

### 前端服务

前端服务使用 Python 内置的 HTTP 服务器提供静态文件服务，运行在 8001 端口。该服务负责提供所有前端页面文件，包括 HTML 页面、CSS 样式表、JavaScript 脚本和图片资源等。

服务启动后，可以通过以下地址访问各页面：首页 http://localhost:8001/index.html、专业详情页 http://localhost:8001/major-detail.html、信息管理页 http://localhost:8001/add-info.html，以及经历分享页 http://localhost:8001/experience-sharing.html。

前端服务默认从项目根目录提供文件，因此所有页面中引用的相对路径资源（如 JavaScript 文件、CSS 文件等）都能正常加载。

### API 服务配置

前端代码通过 `api-service.js` 文件与后端 API 进行通信。该文件中的 `ApiService` 类封装了所有 API 请求方法，并提供了模拟数据作为后备方案。

当前端尝试请求 API 但后端服务不可用时，会自动使用内置的模拟数据，确保页面仍能正常显示基础内容。这对于前端布局和交互逻辑的调试非常方便，无需依赖后端服务即可进行前端开发。

`ApiService` 类支持多种 API 地址配置方式。默认配置指向本地开发环境 http://localhost:8000/api；也可以通过环境变量 `API_URL` 覆盖默认配置；还支持将配置保存到浏览器的 localStorage 中，实现持久化配置。这些配置方式为不同开发场景提供了灵活性。

## API 测试

### 使用测试脚本测试

项目提供了专门的 API 测试脚本 `test-api.py`，可以快速验证后端服务的各项 API 接口是否正常工作。

确保后端服务已启动后，在命令提示符中执行以下命令：

```cmd
cd D:\github.com\carrotmet\zyplusv2
python test-api.py
```

测试脚本会自动依次测试以下接口：根路径测试、获取学科门类、获取专业列表、获取职业列表、搜索专业、创建专业、创建职业、创建个人经历、获取推荐职业以及初始化数据库。测试完成后会显示成功率统计，帮助快速定位问题接口。

### 使用 Swagger UI 测试

FastAPI 自动生成的 Swagger UI 提供了更直观的接口测试方式。启动后端服务后，在浏览器中访问 http://localhost:8000/docs，即可看到交互式的 API 文档页面。

在 Swagger UI 页面中，可以展开任意接口查看详细信息，包括请求参数、响应格式等。点击接口右侧的「Try it out」按钮，可以输入参数并发送请求，查看实际的响应结果。这种方式特别适合探索性测试和接口调试。

### 常见测试场景

**验证数据库初始化**：首次启动后端服务时，数据库为空。可以调用 POST /api/init-data 接口初始化示例数据，包括学科门类、专业、职业和职业路径等信息。

**测试 CRUD 操作**：使用 POST 接口创建数据，GET 接口读取数据，验证数据的增删改查功能是否正常。

**测试搜索功能**：访问 GET /api/majors/search?q=计算机 等接口，验证搜索功能是否按预期工作。

## 故障排除

### 端口被占用

如果启动服务时提示端口被占用，需要找到占用端口的进程并结束它，或者修改服务使用的端口。

识别占用端口的进程，执行以下命令：

```cmd
netstat -ano | findstr :8000
```

这将显示占用 8000 端口的进程信息，包括进程 ID（PID）。记录下 PID 后，执行以下命令结束进程：

```cmd
taskkill /PID <PID> /F
```

如果无法结束占用端口的进程，或者需要使用其他端口，可以在启动命令中指定不同的端口。例如，使用 9000 端口启动后端服务：

```cmd
python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

同时需要修改 api-service.js 中的 baseURL 配置，使其指向新的端口。

### Python 环境问题

如果提示「python 不是内部或外部命令」，说明 Python 未正确安装或未配置环境变量。检查 Python 是否已添加到系统 PATH 环境变量中，可以在命令提示符中执行 `where python` 来验证。

如果存在多个 Python 版本冲突，建议使用 Python 虚拟环境。在 backend 目录下执行以下命令创建和激活虚拟环境：

```cmd
cd D:\github.com\carrotmet\zyplusv2\backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

激活虚拟环境后，后续的 Python 命令都将使用虚拟环境中的 Python 解释器。

### 数据库初始化失败

如果后端服务启动时报告数据库初始化失败，可能是权限问题或磁盘空间不足。确保项目目录有写入权限，特别是 data 目录。

可以尝试手动创建目录并初始化数据库：

```cmd
cd D:\github.com\carrotmet\zyplusv2
mkdir data
cd backend
python -c "from app.database import create_tables; create_tables()"
```

如果仍然失败，检查 data 目录的权限设置，确保当前用户有写入权限。

### 前端无法连接后端

如果前端页面加载后数据无法显示，可能是前端无法连接到后端 API。首先确认后端服务是否正在运行，访问 http://localhost:8000/ 应该返回欢迎信息。

检查浏览器控制台是否有报错信息。如果有 CORS 错误，确保后端服务的 CORS 配置允许前端域名的请求。项目默认配置为允许所有来源（allow_origins=["*"]），适合开发环境使用。

还可以检查 api-service.js 中的 baseURL 配置是否正确。打开浏览器开发者工具，查看网络请求是否发送到正确的地址。

### 服务启动后无响应

如果服务启动后访问无响应，可能是防火墙阻止了连接。检查 Windows 防火墙设置，确保 Python 程序允许通过防火墙。

也可以尝试使用 localhost 之外的地址访问，如 http://127.0.0.1:8000，排除域名解析问题。

## 开发建议

### 使用虚拟环境

强烈建议在 Python 虚拟环境中进行后端开发，以避免不同项目之间的依赖冲突。虚拟环境将项目的依赖与系统全局环境隔离，使项目更具可移植性。

创建虚拟环境后，每次开始开发前请记得激活虚拟环境（执行 `venv\Scripts\activate.bat`），这样安装的包才会进入虚拟环境。开发完成后可以执行 `deactivate` 命令退出虚拟环境。

### 热重载支持

后端服务启动时使用了 `--reload` 参数，支持代码修改后自动重新加载。这意味在对后端代码进行修改后，无需手动重启服务即可看到变更效果。但请注意，对数据库模型（database.py）或模式定义（schemas.py）的修改可能需要完全重启服务才能生效。

### 调试技巧

在开发过程中，可以使用以下技巧提升调试效率：

使用 `print()` 语句在代码中添加调试输出，这些输出会显示在运行后端服务的命令提示符窗口中。FastAPI 的日志信息也会显示在这里，包括每个请求的详细信息。

使用浏览器开发者工具（按 F12 打开）可以查看前端页面的网络请求、控制台输出等信息。如果前端出现问题，这里的报错信息通常能提供有用的线索。

对于复杂的 API 调试，推荐使用 Postman 或 curl 工具，可以更灵活地构造请求、查看响应头和响应体。

### 代码风格

项目遵循以下代码风格约定：

后端 Python 代码使用 PEP 8 风格指南。使用 Black 工具可以自动格式化代码，保持代码风格一致。

前端 JavaScript 代码使用 ESLint 进行代码质量检查。项目中已配置基本的 ESLint 规则，建议在提交代码前运行检查。

所有代码文件使用 UTF-8 编码，并使用 Unix 换行符（LF）。如果使用 VS Code，可以在状态栏中点击「CRLF」切换为「LF」。

## 文件结构

项目根目录下的 Windows 开发相关文件结构如下：

```
D:\github.com\carrotmet\zyplusv2\
├── start-dev.bat          # 一键启动开发环境脚本（推荐使用）
├── start-backend.bat      # 独立启动后端服务脚本
├── start-frontend.bat     # 独立启动前端服务脚本
├── test-api.py            # API 测试脚本
├── api-service.js         # 前端 API 服务配置（已增强）
├── backend/               # 后端代码目录
│   └── app/
│       ├── main.py       # FastAPI 主应用文件
│       ├── database.py   # 数据库模型和初始化
│       ├── schemas.py    # Pydantic 数据模式
│       └── crud.py       # 数据库操作函数
└── doc/                   # 文档目录
    └── WINDOWS_DEVELOPMENT.md  # 本开发指南
    └── MODIFICATIONS.md        # 修改记录文档
```

所有新增的 Windows 开发支持文件都位于项目根目录，不会影响原有的项目结构和功能。原有文件保持不变，确保了向后兼容性。

## 后续维护

### 更新依赖

如果项目的 requirements.txt 文件发生变化，需要更新虚拟环境中的依赖包。在虚拟环境中执行以下命令：

```cmd
pip install -r requirements.txt --upgrade
```

### 备份数据

开发过程中产生的数据存储在 data 目录下的 career_guidance.db 文件中。如果需要备份数据，可以直接复制该文件。如果需要重置数据库，删除该文件后重启后端服务将会重新创建空数据库。

### 清理环境

如果需要清理开发环境，可以执行以下操作：

删除 data 目录重置数据库，删除 logs 目录清除日志文件（如有）。如果使用了虚拟环境，可以删除 backend 目录下的 venv 目录来移除虚拟环境。

注意：清理操作会丢失所有开发过程中添加的数据，请确保不需要这些数据后再执行清理。
