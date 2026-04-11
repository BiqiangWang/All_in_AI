# Agent Chat Platform 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于 Aegra + Agent Chat UI + deepagents 的通用 LangChain Agent 对话平台

**Architecture:** deepagents 作为 LangGraph Graph 接入 Aegra，Aegra 提供 Agent Protocol API 和企业级能力（持久化、流式），Agent Chat UI 作为前端交互界面。开发模式使用 LocalExecutor（无需 Redis），生产模式使用 WorkerExecutor + Redis。

**Tech Stack:** Python 3.12 + .venv, deepagents, Aegra, LangGraph, PostgreSQL, Next.js (Agent Chat UI), Docker Compose

---

## 文件结构

```
D:\Dev\All_in_AI\
├── backend/
│   ├── .venv/                   # Python 虚拟环境
│   ├── deepagents/              # deepagents 源码
│   ├── agents/
│   │   ├── __init__.py
│   │   └── basic_agent.py      # 通用 agent 定义
│   ├── aegra.json               # Aegra 配置
│   ├── .env                     # 环境变量
│   ├── pyproject.toml           # Python 依赖
│   └── scripts/
│       └── init.sh              # 环境初始化脚本
├── frontend/
│   └── (克隆自 agent-chat-ui)
├── docker-compose.yml           # 全量服务编排
├── docker-compose.dev.yml       # 开发模式
└── CLAUDE.md
```

---

## Task 1: 初始化项目结构和后端环境

**Files:**
- Create: `backend/.gitignore`
- Create: `backend/pyproject.toml`
- Create: `backend/.env`
- Create: `backend/scripts/init.sh`
- Create: `backend/agents/__init__.py`

- [ ] **Step 1: 创建 backend 目录结构**

```bash
mkdir -p D:/Dev/All_in_AI/backend/agents
mkdir -p D:/Dev/All_in_AI/backend/scripts
```

- [ ] **Step 2: 创建 backend/.gitignore**

```
.venv/
__pycache__/
*.pyc
.env
*.egg-info/
dist/
build/
```

- [ ] **Step 3: 创建 backend/pyproject.toml**

```toml
[project]
name = "agent-chat-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "deepagents",
    "aegra-api",
    "langgraph",
    "langchain-openai",
    "langchain-anthropic",
    "python-dotenv",
    "psycopg2-binary",
    "asyncpg",
]
```

- [ ] **Step 4: 创建 backend/.env**

```
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aegra
REDIS_BROKER_ENABLED=false
AEGRA_API_PORT=2026
```

- [ ] **Step 5: 创建 backend/scripts/init.sh**

```bash
#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Creating Python virtual environment..."
python -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install deepagents aegra-api
pip install -e ./deepagents 2>/dev/null || true

echo "Installing additional dependencies..."
pip install langgraph langchain-openai python-dotenv asyncpg

echo "Setup complete!"
echo "Run 'source .venv/bin/activate' to activate the environment"
```

- [ ] **Step 6: 创建 backend/agents/__init__.py**

```python
"""Agent definitions for Aegra."""
```

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "chore: initialize project structure and backend scaffolding"
```

---

## Task 2: 配置 deepagents 和创建基础 Agent

**Files:**
- Create: `backend/agents/basic_agent.py`
- Modify: `backend/aegra.json`
- Create: `backend/deepagents/` (clone or submodule)

- [ ] **Step 1: 克隆 deepagents 到 backend/deepagents**

```bash
cd D:/Dev/All_in_AI/backend
git clone https://github.com/langchain-ai/deepagents.git deepagents
```

- [ ] **Step 2: 查看 deepagents 的 graph 导出格式**

```bash
ls -la D:/Dev/All_in_AI/backend/deepagents/
cat D:/Dev/All_in_AI/backend/deepagents/README.md | head -100
```

- [ ] **Step 3: 创建 backend/agents/basic_agent.py**

```python
"""Basic conversational agent using deepagents."""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


def create_basic_agent(model_name: str = "gpt-4o") -> dict:
    """Create a basic ReAct agent.

    Args:
        model_name: The model to use for the agent.

    Returns:
        A dict containing the graph and metadata.
    """
    # Choose model based on name
    if "claude" in model_name.lower():
        model = ChatAnthropic(model=model_name)
    else:
        model = ChatOpenAI(model=model_name)

    # Create ReAct agent using LangGraph's prebuilt agent
    graph = create_react_agent(model, [])

    return {
        "graph": graph,
        "name": "basic-agent",
        "description": "A basic conversational agent powered by deepagents and LangChain",
    }


# For Aegra loading, export graph
def get_graph():
    """Factory function for Aegra to load the graph."""
    agent = create_basic_agent()
    return agent["graph"]


# Export graph (for static loading)
graph = get_graph()
```

- [ ] **Step 4: 创建 backend/aegra.json**

```json
{
  "$schema": "https://docs.aegra.dev/schema.json",
  "graphs": {
    "basic-agent": {
      "path": "agents.basic_agent",
      "name": "basic-agent",
      "description": "A basic conversational agent"
    }
  },
  "auth": {
    "enabled": false
  },
  "http": {
    "port": 2026,
    "cors": {
      "allow_origins": ["http://localhost:3000"],
      "allow_credentials": true
    }
  },
  "store": {
    "enabled": false
  },
  "observability": {
    "enabled": false
  }
}
```

- [ ] **Step 5: 验证 agent 定义可以被导入**

```bash
cd D:/Dev/All_in_AI/backend
source .venv/bin/activate
python -c "from agents.basic_agent import graph; print('Graph loaded successfully:', type(graph))"
```

- [ ] **Step 6: Commit**

```bash
git add backend/agents/ backend/aegra.json
git commit -m "feat: add basic agent definition and Aegra config"
```

---

## Task 3: 克隆和配置 Agent Chat UI 前端

**Files:**
- Create: `frontend/` (clone from agent-chat-ui)
- Create: `frontend/.env.local`
- Modify: `frontend/next.config.mjs` (if needed)

- [ ] **Step 1: 克隆 agent-chat-ui 到 frontend**

```bash
cd D:/Dev/All_in_AI
git clone https://github.com/langchain-ai/agent-chat-ui.git frontend
```

- [ ] **Step 2: 创建 frontend/.env.local**

```
NEXT_PUBLIC_API_URL=http://localhost:2026
NEXT_PUBLIC_ASSISTANT_ID=basic-agent
NEXT_PUBLIC_AUTH_SCHEME=
```

- [ ] **Step 3: 安装前端依赖**

```bash
cd D:/Dev/All_in_AI/frontend
pnpm install
```

- [ ] **Step 4: Commit frontend as initial state**

```bash
git add frontend/
git commit -m "chore: add Agent Chat UI frontend"
```

---

## Task 4: 创建 Docker Compose 配置

**Files:**
- Create: `docker-compose.yml`
- Create: `docker-compose.dev.yml`
- Create: `Dockerfile.backend`

- [ ] **Step 1: 创建 docker-compose.yml（生产模式）**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: aegra
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    ports:
      - "2026:2026"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/aegra
      REDIS_BROKER_ENABLED: "true"
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: aegra serve

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:2026
      NEXT_PUBLIC_ASSISTANT_ID: basic-agent
    depends_on:
      - backend

volumes:
  postgres_data:
```

- [ ] **Step 2: 创建 docker-compose.dev.yml（开发模式，无 Redis）**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: aegra
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    ports:
      - "2026:2026"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/aegra
      REDIS_BROKER_ENABLED: "false"
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: aegra dev

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:2026
      NEXT_PUBLIC_ASSISTANT_ID: basic-agent
    depends_on:
      - backend

volumes:
  postgres_data:
```

- [ ] **Step 3: 创建 backend/Dockerfile.backend**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --all-packages

EXPOSE 2026

CMD ["aegra", "dev"]
```

- [ ] **Step 4: 创建 frontend/Dockerfile.frontend**

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN npm install -g pnpm && pnpm install

# Copy source files
COPY . .

EXPOSE 3000

CMD ["pnpm", "dev"]
```

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml docker-compose.dev.yml backend/Dockerfile.backend
git commit -m "chore: add Docker Compose configuration for dev and prod"
```

---

## Task 5: 创建 CLAUDE.md 项目上下文文件

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: 创建 CLAUDE.md**

```markdown
# CLAUDE.md

This file provides context for AI coding agents working with this repository.

## Project Overview

**Agent Chat Platform** 是一个基于 Aegra + Agent Chat UI + deepagents 构建的通用 LangChain Agent 对话平台。

- **Aegra**: 后端 API 服务（Agent Protocol 兼容）
- **Agent Chat UI**: Next.js 前端交互界面
- **deepagents**: Agent 开发框架

## 项目结构

```
├── backend/              # Python 后端
│   ├── agents/           # Agent 定义
│   ├── deepagents/       # deepagents 源码
│   ├── aegra.json        # Aegra 配置
│   ├── .env              # 环境变量
│   └── pyproject.toml    # Python 依赖
├── frontend/             # Next.js 前端 (Agent Chat UI)
├── docker-compose.yml    # 生产环境
├── docker-compose.dev.yml # 开发环境
└── docs/                 # 设计文档和计划
```

## 快速开始

### 开发模式

```bash
# 1. 启动 PostgreSQL
docker compose -f docker-compose.dev.yml up -d postgres

# 2. 启动后端
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install deepagents aegra-api
aegra dev

# 3. 启动前端（新终端）
cd frontend
pnpm install
pnpm dev
```

访问 http://localhost:3000 配置 Deployment URL (http://localhost:2026) 和 Assistant ID (basic-agent)。

### 生产模式

```bash
docker compose up --build
```

## 关键配置

- `backend/aegra.json`: 定义加载的 graph
- `backend/.env`: API keys 和数据库连接
- `frontend/.env.local`: 前端配置
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md project context"
```

---

## Task 6: 验证完整流程

- [ ] **Step 1: 确保 PostgreSQL 运行**

```bash
docker compose -f docker-compose.dev.yml up -d postgres
sleep 5
docker compose -f docker-compose.dev.yml ps
```

- [ ] **Step 2: 启动后端并验证健康状态**

```bash
cd D:/Dev/All_in_AI/backend
source .venv/bin/activate
aegra dev &
sleep 10
curl -s http://localhost:2026/health
```

预期输出包含 `"status": "healthy"`

- [ ] **Step 3: 测试 Agent Protocol API**

```bash
# 获取 assistants
curl -s http://localhost:2026/assistants | python -m json.tool

# 创建 thread
curl -s -X POST http://localhost:2026/threads \
  -H "Content-Type: application/json" \
  -d '{}' | python -m json.tool
```

- [ ] **Step 4: 启动前端并验证**

```bash
cd D:/Dev/All_in_AI/frontend
pnpm dev &
sleep 10
curl -s http://localhost:3000 | head -20
```

- [ ] **Step 5: 在浏览器中验证完整流程**

1. 打开 http://localhost:3000
2. 输入 Deployment URL: http://localhost:2026
3. 输入 Assistant ID: basic-agent
4. 开始对话测试

---

## 实施检查清单

- [ ] Task 1: 项目结构和后端环境
- [ ] Task 2: deepagents 配置和基础 Agent
- [ ] Task 3: Agent Chat UI 前端
- [ ] Task 4: Docker Compose 配置
- [ ] Task 5: CLAUDE.md
- [ ] Task 6: 完整流程验证
