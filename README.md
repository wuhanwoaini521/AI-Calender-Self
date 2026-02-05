# AI Calendar 🗓️🤖

一个具有 AI 助手功能的智能日历应用，使用 **React 19 + TypeScript** 前端和 **Python FastAPI** 后端构建。

## ✨ 核心功能

### 日历功能
- 📅 **多视图日历**：月视图、周视图、日视图
- 📝 **事件管理**：创建、编辑、删除日程事件
- 🎨 **颜色编码**：8 种颜色用于事件分类
- 🔍 **事件查询**：按日期范围查看事件

### AI 助手功能
- 🤖 **智能对话**：通过自然语言与 AI 交互
- 🛠️ **工具调用**：AI 可直接操作日历（创建/更新/删除事件）
- 🧠 **技能系统**：支持多步骤复杂任务
- 🔌 **MCP 支持**：Model Context Protocol 协议支持
- ⚡ **流式响应**：实时返回 AI 处理结果

### 认证与安全
- 🔐 **JWT 认证**：安全的用户会话管理
- 👤 **用户管理**：注册、登录、个人资料

## 🚀 快速开始

### 启动后端服务

```bash
./start_server.sh
```

或手动启动：
```bash
cd server
pip install -r requirements.txt
python run.py
```

后端服务将在 `http://localhost:3001` 启动
- API 文档：http://localhost:3001/docs
- 健康检查：http://localhost:3001/health

### 启动前端开发服务器

```bash
npm install
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 构建生产版本

```bash
npm run build
```

## 📁 项目结构

```
.
├── src/                          # 前端源码
│   ├── App.tsx                   # 主应用组件
│   ├── main.tsx                  # React 入口
│   ├── ai/                       # AI 助手组件
│   │   └── AIAssistant.tsx
│   ├── calendar/                 # 日历视图组件
│   │   ├── MonthView.tsx
│   │   ├── WeekView.tsx
│   │   ├── DayView.tsx
│   │   └── EventDialog.tsx
│   ├── components/               # 共享组件
│   │   ├── AuthDialog.tsx
│   │   ├── Header.tsx
│   │   └── ui/                   # shadcn/ui 组件（50+）
│   ├── hooks/                    # 自定义 React Hooks
│   │   ├── useAuth.ts
│   │   ├── useCalendar.ts
│   │   ├── useAI.ts
│   │   └── useAIV2.ts            # AI v2 Hook
│   ├── services/                 # API 服务
│   │   └── api.ts
│   └── types/                    # TypeScript 类型定义
│       └── index.ts
├── server/                       # Python FastAPI 后端
│   ├── app/
│   │   ├── core/                 # 核心模块
│   │   │   ├── config.py         # 配置
│   │   │   └── security.py       # JWT & 密码哈希
│   │   ├── models/               # 数据模型
│   │   │   ├── schemas.py        # Pydantic 模型
│   │   │   └── database.py       # 内存数据库
│   │   ├── routers/              # API 路由
│   │   │   ├── auth.py           # 认证
│   │   │   ├── events.py         # 事件管理
│   │   │   ├── ai.py             # AI v1
│   │   │   └── ai_v2.py          # AI v2（工具/技能）
│   │   ├── services/             # 业务逻辑
│   │   │   ├── ai_service.py     # AI v1 服务
│   │   │   ├── ai_service_v2.py  # AI v2 服务
│   │   │   └── ai_service_v2_pure_fc.py
│   │   ├── tools/                # 工具系统
│   │   │   ├── base.py
│   │   │   ├── calendar_tools.py # 日历工具
│   │   │   ├── schedule_tools.py # 日程工具
│   │   │   ├── notification_tools.py
│   │   │   └── registry.py
│   │   ├── skills/               # 技能系统
│   │   │   ├── base.py
│   │   │   ├── calendar_skills.py
│   │   │   ├── meeting_assistant_skill.py
│   │   │   └── registry.py
│   │   └── mcp/                  # MCP 协议
│   │       ├── protocol.py
│   │       └── server.py
│   ├── requirements.txt
│   └── run.py
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── components.json               # shadcn/ui 配置
```

## 🛠️ 技术栈

### 前端
- **框架**：React 19 + TypeScript 5.9
- **构建工具**：Vite 7
- **样式**：Tailwind CSS 3.4 + CSS 变量
- **UI 组件**：shadcn/ui + Radix UI
- **表单**：react-hook-form + Zod 验证
- **日期处理**：date-fns
- **图标**：lucide-react
- **Toast 通知**：sonner

### 后端
- **框架**：FastAPI 0.109
- **服务器**：Uvicorn 0.27
- **认证**：python-jose (JWT) + passlib (bcrypt)
- **数据验证**：Pydantic 2.5 + pydantic-settings
- **日期/时间**：python-dateutil
- **数据库**：内存数据库（Python 字典）
- **AI 集成**：OpenAI 兼容 API（支持 OpenRouter 等）

## 📡 API 端点

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息
- `PUT /api/auth/profile` - 更新用户信息

### 事件管理
- `GET /api/events` - 获取事件列表（支持 view, date 查询参数）
- `POST /api/events` - 创建事件
- `GET /api/events/{id}` - 获取单个事件
- `PUT /api/events/{id}` - 更新事件
- `DELETE /api/events/{id}` - 删除事件
- `GET /api/events/upcoming` - 获取即将发生的事件

### AI 助手 v1（传统）
- `POST /api/ai/chat` - 与 AI 对话
- `GET /api/ai/insights` - 获取 AI 洞察
- `PUT /api/ai/insights/{id}/read` - 标记洞察为已读
- `GET /api/ai/suggestions` - 获取每日建议
- `POST /api/ai/schedule` - 生成优化日程

### AI 助手 v2（工具/技能/MCP）
- `POST /api/ai/v2/chat` - 流式对话（支持工具调用）
- `GET /api/ai/v2/tools` - 列出可用工具
- `POST /api/ai/v2/tools/call` - 直接调用工具
- `GET /api/ai/v2/skills` - 列出可用技能
- `POST /api/ai/v2/skills/call` - 直接调用技能
- `POST /api/ai/v2/mcp` - MCP 协议端点

## 🧰 AI 工具列表

| 工具名 | 描述 |
|--------|------|
| `create_event` | 创建新日历事件 |
| `get_events` | 查询指定日期范围的事件 |
| `update_event` | 更新已有事件 |
| `delete_event` | 删除事件 |
| `find_free_slots` | 查找空闲时间段 |
| `detect_conflicts` | 检测日程冲突 |
| `generate_schedule` | 生成优化日程 |
| `optimize_schedule` | 分析并建议日程优化 |
| `suggest_breaks` | 建议休息时间 |

## 🎓 AI 技能列表

| 技能名 | 描述 |
|--------|------|
| `schedule_management` | 日程管理（查看/分析日程）|
| `meeting_planning` | 会议规划（查找合适时间）|
| `daily_planning` | 日常规划（生成每日计划）|

## 🔧 配置

### 前端环境变量
```bash
VITE_API_URL=http://localhost:3001/api  # 后端 API 地址
```

### 后端环境变量（`server/.env`）
```env
# 安全
SECRET_KEY=your-secret-key-here

# CORS
FRONTEND_URL=http://localhost:5173

# 服务器
DEBUG=True
PORT=3001

# AI 配置（OpenAI 兼容 API）
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 或 OpenRouter 等
OPENAI_MODEL=gpt-4o-mini
```

## 📦 依赖

### Python 依赖
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
python-dateutil==2.8.2
openai==1.12.0
```

### NPM 依赖
主要依赖包括：
- React 19, React DOM 19
- TypeScript ~5.9.3
- Vite 7.2.4
- Tailwind CSS 3.4.19
- Radix UI 组件库
- date-fns, lucide-react, sonner 等

完整依赖列表请查看 `package.json`

## 🎯 使用示例

### 通过 AI 创建事件
用户可以说：
- "明天下午三点开会"
- "帮我创建一个明天上午9点的会议"
- "后天晚上8点聚餐"

AI 会自动：
1. 解析时间表达
2. 调用 `create_event` 工具
3. 返回创建结果

### 查询日程
- "我今天有什么安排？"
- "查看这周的日程"
- "明天有什么会？"

### 查找空闲时间
- "我明天什么时候有空？"
- "帮我找个 1 小时的空闲时间"

## 🔒 安全注意事项

1. **JWT 令牌**：令牌默认 7 天过期
2. **CORS**：配置为只允许特定前端域名
3. **密码哈希**：使用 bcrypt 通过 passlib
4. **输入验证**：所有输入通过 Pydantic 验证
5. **开发环境**：默认不使用 HTTPS，生产环境请启用

## 📝 开发指南

### 添加新工具
1. 在 `server/app/tools/` 创建工具类，继承 `Tool`
2. 定义 `name`, `description`, `parameters`
3. 实现 `execute` 方法
4. 在 `server/app/initializers.py` 注册工具

### 添加新技能
1. 在 `server/app/skills/` 创建技能类，继承 `Skill`
2. 定义 `name`, `description`, `tools`
3. 实现 `execute` 方法
4. 在 `server/app/initializers.py` 注册技能

### 添加 UI 组件
1. 检查 shadcn/ui 组件库：`npx shadcn add <component>`
2. 或创建自定义组件在 `src/components/`

## 🐛 故障排除

### 后端启动失败
- 检查 `.env` 文件是否存在并配置正确
- 确认端口 3001 未被占用
- 检查 Python 依赖是否安装完整

### 前端构建失败
- 确认 Node.js 版本兼容
- 删除 `node_modules` 并重新运行 `npm install`
- 检查 TypeScript 类型错误：`npx tsc --noEmit`

### AI 功能不工作
- 检查 `OPENAI_API_KEY` 是否配置
- 确认 `OPENAI_BASE_URL` 可访问
- 查看后端日志获取详细错误信息

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**提示**：项目使用内存数据库，重启后端后数据会丢失。如需持久化，请修改 `server/app/models/database.py` 添加数据库支持。