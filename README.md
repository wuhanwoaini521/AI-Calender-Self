# Calendar MCP Backend

一个基于 FastAPI + MCP (Model Context Protocol) + Skills 的智能日历管理后端服务。支持通过自然语言对话来管理日程，创建单次或重复事件。

## ✨ 主要特性

- 🤖 **AI 对话管理日历** - 通过自然语言与日历交互
- 📅 **智能时间解析** - 自动识别"明天"、"后天"、"下周一"等相对时间
- 🔄 **重复事件支持** - 支持每天、每周特定天数、每月重复的日程
- 🛠️ **MCP 工具调用** - 基于 Model Context Protocol 的工具调用架构
- 📝 **Skills 系统** - 可扩展的 Skill 文档支持
- 🚀 **FastAPI 驱动** - 高性能异步 API
- 📚 **自动 API 文档** - 内置 Swagger/ReDoc 文档

## 🏗️ 项目架构

```
AI-Calender-Self/
├── app/                    # 主应用目录
│   ├── api/               # API 路由层
│   │   └── routes.py      # API 端点定义
│   ├── models/            # 数据模型
│   │   ├── calendar.py    # 日历事件模型
│   │   └── chat.py        # 对话模型
│   ├── services/          # 业务逻辑层
│   │   ├── calendar_service.py  # 日历 CRUD 服务
│   │   └── chat_service.py      # AI 对话服务
│   ├── mcp/               # MCP 协议实现
│   │   ├── server.py      # MCP 服务器
│   │   └── tools.py       # 工具定义
│   ├── skills/            # Skills 系统
│   │   └── loader.py      # Skill 加载器
│   ├── config.py          # 配置管理
│   └── main.py            # FastAPI 入口
├── Makefile               # 快捷命令
├── pyproject.toml         # 项目依赖
└── .env                   # 环境变量配置
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - Python 包管理器

### 2. 安装依赖

```bash
# 安装依赖
uv sync
```

### 3. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，添加你的 API Key
API_KEY=your_api_key_here
```

### 4. 启动服务

```bash
# 使用 Makefile 启动
make run

# 或使用 uv 直接启动
uv run uvicorn app.main:app --reload
```

服务启动后访问 http://localhost:8000/docs 查看 API 文档。

## 📡 API 接口

### 对话接口

**POST** `/api/chat`

通过自然语言管理日历：

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "message": "帮我创建一个明天下午3点的团队会议",
    "conversation_history": []
  }'
```

### 事件管理接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/events` | 获取事件列表（支持筛选） |
| POST | `/api/events` | 创建新事件 |
| GET | `/api/events/{id}` | 获取单个事件 |
| PUT | `/api/events/{id}` | 更新事件 |
| DELETE | `/api/events/{id}` | 删除事件 |

### 工具和技能接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/tools` | 获取可用 MCP 工具列表 |
| GET | `/api/skills` | 获取可用 Skills 列表 |

## 💬 使用示例

### 创建单次事件

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "message": "帮我创建一个后天下午2点的项目评审会议",
    "conversation_history": []
  }'
```

### 创建重复事件（每周一到周五）

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "message": "帮我创建一个每周一到周五晚上五点半的固定会议",
    "conversation_history": []
  }'
```

### 查询事件

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "message": "显示我本周的所有日程",
    "conversation_history": []
  }'
```

## ⚙️ 配置说明

编辑 `.env` 文件配置以下选项：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `API_KEY` | Kimi API Key | - |
| `API_BASE_URL` | API 基础地址 | https://api.moonshot.cn/v1 |
| `MODEL` | 使用的模型 | moonshot-v1-8k |
| `DEBUG` | 调试模式 | true |
| `APP_NAME` | 应用名称 | Calendar MCP Backend |

支持的模型：
- `moonshot-v1-8k`
- `moonshot-v1-32k`
- `moonshot-v1-128k`

## 🛠️ 可用命令

```bash
# 查看所有命令
make help

# 启动服务
make run

# 安装依赖
make install

# 清理缓存
make clean
```

## 🔧 开发指南

### 添加新的 MCP 工具

1. 在 `app/mcp/tools.py` 中添加工具定义
2. 在 `app/mcp/server.py` 中实现工具执行逻辑

### 添加新的 Skill

1. 在 `app/skills/` 目录下创建 Skill 文件
2. 更新 `app/skills/loader.py` 加载新 Skill

### 添加新的 API 端点

1. 在 `app/api/routes.py` 中定义路由
2. 在 `app/services/` 中添加对应的业务逻辑

## 📚 技术栈

- **FastAPI** - Web 框架
- **Pydantic** - 数据验证
- **OpenAI SDK** - AI API 调用
- **uv** - Python 包管理
- **MCP** - Model Context Protocol

## 📝 License

MIT License
