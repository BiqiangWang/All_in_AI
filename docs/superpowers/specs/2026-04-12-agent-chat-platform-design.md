# Agent Chat Platform 设计文档

## 1. 概述

**项目目标**：基于 Aegra（后端 API）+ Agent Chat UI（前端）+ deepagents（agent 开发框架）构建一个通用 LangChain Agent 对话平台。

**核心思路**：deepagents 作为 LangGraph Graph 接入 Aegra，Aegra 提供 Agent Protocol API 和企业级能力（持久化、流式、监控），Agent Chat UI 作为前端交互界面。

## 2. 技术栈

| 组件 | 技术 | 作用 |
|------|------|------|
| Agent 框架 | deepagents + LangChain | Agent 逻辑（推理、工具调用） |
| 后端 API | Aegra (FastAPI) | Agent Protocol 兼容 API |
| 数据库 | PostgreSQL | 持久化（threads, runs, checkpoints） |
| 消息队列 | Redis | 任务队列（生产环境模式） |
| 前端 | Agent Chat UI (Next.js) | 用户交互界面 |
| 环境管理 | .venv | Python 虚拟环境 |

## 3. 项目结构

```
D:\Dev\All_in_AI\
├── backend/
│   ├── .venv/                   # Python 虚拟环境（.gitignore）
│   ├── deepagents/              # deepagents 源码（可作为 git submodule）
│   ├── agents/
│   │   ├── __init__.py
│   │   └── basic_agent.py       # 通用 agent 定义
│   ├── aegra.json               # Aegra 配置
│   ├── .env                     # 环境变量（API keys 等）
│   ├── pyproject.toml           # Python 依赖
│   └── scripts/
│       └── init_db.sh           # 数据库初始化脚本
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── .env.local               # 前端环境变量
│   └── ...
├── docker-compose.yml           # 全量服务编排
├── docker-compose.dev.yml       # 开发模式（无 Redis）
└── CLAUDE.md                    # 项目上下文
```

## 4. 各组件职责

### 4.1 deepagents + agents/
- 定义 agent 逻辑（StateGraph）
- 导出 `graph` 变量供 Aegra 加载
- 支持工具注册（后续扩展）

### 4.2 Aegra (backend/)
- **API 层**：Agent Protocol 端点（/assistants, /threads, /runs）
- **执行层**：LocalExecutor（开发模式）或 WorkerExecutor（生产模式）
- **持久层**：PostgreSQL（LangGraph checkpoints + metadata）
- **配置**：aegra.json 定义加载哪个 graph

### 4.3 Agent Chat UI (frontend/)
- 通过 Agent Protocol 连接 Aegra API
- 支持流式输出展示
- 提供部署 URL 和 Assistant ID 配置

## 5. 服务通信

```
┌─────────────────┐     Agent Protocol      ┌─────────────────┐
│  Agent Chat UI  │ ──────────────────────► │  Aegra API      │
│  (Next.js)      │ ◄────────────────────── │  (FastAPI)      │
└─────────────────┘     SSE Streaming       └────────┬────────┘
                                                     │
                                          ┌──────────▼──────────┐
                                          │  deepagents Graph    │
                                          │  (StateGraph)        │
                                          └──────────┬──────────┘
                                                     │
                                          ┌──────────▼──────────┐
                                          │  PostgreSQL         │
                                          │  (checkpoints)       │
                                          └─────────────────────┘
```

开发模式下：Redis 可选（使用 LocalExecutor）。
生产模式下：Redis 作为任务队列 broker。

## 6. 环境变量

### backend/.env
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aegra
REDIS_BROKER_ENABLED=false  # 开发模式
AEGRA_API_PORT=2026
```

### frontend/.env.local
```
NEXT_PUBLIC_API_URL=http://localhost:2026
NEXT_PUBLIC_ASSISTANT_ID=basic-agent
NEXT_PUBLIC_AUTH_SCHEME=
```

## 7. 启动流程

### 开发模式
```bash
# 1. 启动 PostgreSQL
docker compose -f docker-compose.yml up -d postgres

# 2. 安装后端依赖
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install deepagents aegra-api
pip install -e ./deepagents
pip install -e ./agents

# 3. 配置 Aegra
cp .env.example .env
# 编辑 .env 填入 API key

# 4. 启动 Aegra
aegra dev  # 同时运行数据库迁移 + 热重载

# 5. 启动前端（新终端）
cd frontend
pnpm install
pnpm dev
```

### 生产模式
```bash
docker compose up --build
```

## 8. 后续扩展方向

1. **工具扩展**：在 deepagents agent 中注册自定义工具（搜索、代码执行等）
2. **多 Agent**：在 aegra.json 配置多个 graph，支持不同场景
3. **Human-in-the-loop**：通过 Aegra 的 approval gate 实现人工审核
4. **监控集成**：对接 Langfuse/Phoenix 进行 Tracing

## 9. 已知约束

- deepagents 需要确认与 LangGraph 的接口兼容性（graph 导出格式）
- Agent Chat UI 连接生产部署时需要配置认证（参考其文档的 API Passthrough 方案）
