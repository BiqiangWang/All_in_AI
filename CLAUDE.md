# CLAUDE.md

This file provides context for AI coding agents working with this repository.

## Project Overview

**Agent Chat Platform** 是一个基于 Aegra + Agent Chat UI + deepagents 构建的通用 LangChain Agent 对话平台。

- **Aegra**: 后端 API 服务（Agent Protocol 兼容）
- **Agent Chat UI**: Next.js 前端交互界面
- **deepagents**: Agent 开发框架（版本 0.4.4）
- **Python 环境**: conda langchain-next (Python 3.12.11)

## 项目结构

```
D:\Dev\All_in_AI\
├── backend/              # Python 后端
│   ├── agents/           # Agent 定义
│   │   └── basic_agent.py  # deepagents create_deep_agent 实现
│   ├── deepagents/       # deepagents 源码（如需修改）
│   ├── aegra.json       # Aegra 配置
│   ├── .env             # 环境变量
│   ├── pyproject.toml   # Python 依赖
│   ├── scripts/
│   │   └── init.sh      # 环境初始化脚本
│   └── Dockerfile.backend
├── frontend/             # Next.js 前端 (Agent Chat UI)
├── docker-compose.yml    # 生产环境
├── docker-compose.dev.yml # 开发环境
└── docs/                 # 设计文档和计划
```

## 快速开始

### 前置要求
- conda 环境 langchain-next 已激活
- Docker Desktop 运行中
- PostgreSQL 可用

### 开发模式

```bash
# 1. 启动 PostgreSQL
docker compose -f docker-compose.dev.yml up -d postgres

# 2. 激活 conda 环境
conda activate langchain-next

# 3. 启动后端（Aegra）
cd backend
conda run -n langchain-next aegra dev

# 4. 启动前端（新终端）
cd frontend
pnpm install  # 首次需要
pnpm dev
```

访问 http://localhost:3000 配置：
- Deployment URL: http://localhost:2026
- Assistant ID: basic-agent

### 生产模式

```bash
docker compose up --build
```

## 关键配置

- `backend/aegra.json`: 定义加载的 graph
- `backend/.env`: API keys 和数据库连接
- `frontend/.env.local`: 前端配置
- `backend/agents/basic_agent.py`: 使用 `deepagents.create_deep_agent` 创建 agent

## Agent 开发

在 `backend/agents/basic_agent.py` 中定义 agent：

```python
from deepagents import create_deep_agent

def create_basic_agent(model_name: str = "gpt-4o") -> dict:
    model = ChatOpenAI(model=model_name)
    graph = create_deep_agent(model=model, tools=[])
    return {"graph": graph, "name": "basic-agent", ...}
```

修改后重启 Aegra 后端即可生效。
