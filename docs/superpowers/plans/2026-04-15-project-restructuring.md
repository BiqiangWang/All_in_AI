# 项目重构实施计划

> **目标：** 将项目重构为三层独立架构（agents/、backend/、frontend/）

**架构说明：**
- `agents/` - Python 包，从 `backend/agents/` 迁移过来，包含 agent 逻辑、工具、记忆、skills
- `backend/` - Aegra API 服务，从 `D:\Dev\github\aegra` 复制过来
- `frontend/` - Next.js 前端（位置不变）

---

## 目标目录结构

```
D:\Dev\All_in_AI\
├── agents/                          # Python 包（从 backend/agents/ 迁移）
│   ├── pyproject.toml
│   ├── src/agents/
│   │   ├── __init__.py
│   │   ├── basic_agent.py          # 重命名自 basic_agent.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── memory.py
│   │   │   └── search_web.py
│   │   ├── skills/                  # SKILL.md 文件
│   │   ├── memory/                  # 记忆系统
│   │   │   ├── __init__.py
│   │   │   ├── file_provider.py
│   │   │   ├── memory_manager.py
│   │   │   └── provider.py
│   │   └── prompt/
│   │       └── system_prompt.txt
│   └── tests/
│
├── backend/                         # Aegra API 服务（从 aegra 源码复制）
│   ├── agents/                      # 我们的 agent 配置
│   │   ├── __init__.py
│   │   ├── aegra.json              # Aegra graph 配置
│   │   └── basic_agent.py          # 引用 agents 包
│   ├── libs/
│   │   ├── aegra-api/
│   │   └── aegra-cli/
│   ├── .env                         # 环境变量
│   ├── pyproject.toml               # workspace 配置
│   ├── Dockerfile.backend
│   └── docker-compose.yml
│
├── frontend/                        # 不变
│
└── docker-compose.yml               # 更新路径
```

---

## 任务 1: 备份当前 backend/agents

**文件:**
- 备份: `backend/agents/` → `_backup/agents/`
- 备份: `backend/memory/` → `_backup/memory/`
- 备份: `backend/.env` → `_backup/.env`

- [ ] **Step 1: 创建备份**

```bash
mkdir -p D:/Dev/All_in_AI/_backup
cp -r D:/Dev/All_in_AI/backend/agents D:/Dev/All_in_AI/_backup/
cp -r D:/Dev/All_in_AI/backend/memory D:/Dev/All_in_AI/_backup/
cp D:/Dev/All_in_AI/backend/.env D:/Dev/All_in_AI/_backup/
```

---

## 任务 2: 创建 agents Python 包

**文件:**
- 创建: `agents/pyproject.toml`
- 创建: `agents/src/agents/__init__.py`
- 移动: `_backup/agents/` → `agents/src/agents/`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p D:/Dev/All_in_AI/agents/src/agents
```

- [ ] **Step 2: 创建 pyproject.toml**

```toml
[project]
name = "agents"
version = "0.1.0"
description = "All-in-AI Agent package"
requires-python = ">=3.12"
dependencies = [
    "deepagents>=0.4.0",
    "langchain-anthropic",
    "langchain-openai",
    "langchain-core",
    "pydantic",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/agents"]
```

- [ ] **Step 3: 移动并整理文件**

```bash
# 移动 agents 内容
mv D:/Dev/All_in_AI/_backup/agents/* D:/Dev/All_in_AI/agents/src/agents/

# 移动 memory 内容
mv D:/Dev/All_in_AI/_backup/memory D:/Dev/All_in_AI/agents/src/agents/memory
```

- [ ] **Step 4: 更新 basic_agent.py 导入**

修改 `agents/src/agents/basic_agent.py` 中的导入：
```python
# 更改:
from agents.tools import search_web, memory

# 为:
from agents.tools import search_web, memory
```
（memory import 已经是正确的相对路径，无需修改）

- [ ] **Step 5: 创建 __init__.py**

```python
"""All-in-AI Agents package."""
from agents.basic_agent import create_basic_agent, get_skills_metadata

__all__ = ["create_basic_agent", "get_skills_metadata"]
```

- [ ] **Step 6: 验证**

```bash
cd D:/Dev/All_in_AI
python -c "import sys; sys.path.insert(0, 'agents/src'); from agents import create_basic_agent; print('OK')"
```

---

## 任务 3: 创建 backend（Aegra 源码）

**文件:**
- 复制: `D:\Dev\github\aegra` → `backend/`
- 更新: `backend/.env`（从备份恢复）
- 更新: `backend/agents/basic_agent.py`（引用 agents 包）
- 更新: `backend/pyproject.toml`（workspace 配置）

- [ ] **Step 1: 备份当前 backend 并创建新的 backend**

```bash
# 先备份当前 backend（包含我们的配置）
cp -r D:/Dev/All_in_AI/backend D:/Dev/All_in_AI/_backup/backend_original

# 复制 Aegra 源码到 backend
cp -r D:/Dev/github/aegra D:/Dev/All_in_AI/backend_new
rm -rf D:/Dev/All_in_AI/backend
mv D:/Dev/All_in_AI/backend_new D:/Dev/All_in_AI/backend
```

- [ ] **Step 2: 恢复 .env 和 agents 配置**

```bash
# 恢复 .env
cp D:/Dev/All_in_AI/_backup/.env D:/Dev/All_in_AI/backend/

# 在 backend/ 中创建 agents 目录（我们的 agent 配置）
mkdir -p D:/Dev/All_in_AI/backend/agents
```

- [ ] **Step 3: 更新 backend/pyproject.toml**

添加 workspace 配置引用 agents 包：

```toml
[tool.uv.workspace]
members = ["libs/*", "../agents"]

[project]
dependencies = [
    "agents",
]
```

- [ ] **Step 4: 创建 backend/agents/basic_agent.py**

创建 `backend/agents/basic_agent.py`，导入并使用 agents 包：

```python
"""Aegra graph configuration for All-in-AI."""
import sys
from pathlib import Path

# Add agents package to path
_agents_src = Path(__file__).parent.parent.parent / "agents" / "src"
if str(_agents_src) not in sys.path:
    sys.path.insert(0, str(_agents_src))

from agents import create_basic_agent

def get_graph():
    return create_basic_agent()["graph"]

# For Aegra loading
graph = get_graph()
```

- [ ] **Step 5: 创建 backend/agents/aegra.json**

```json
{
  "graphs": {
    "all-in-ai": "./agents/basic_agent.py:graph"
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
  }
}
```

- [ ] **Step 6: 创建 backend/agents/__init__.py**

```python
"""All-in-AI agent configuration for Aegra."""
```

- [ ] **Step 7: 验证**

```bash
cd D:/Dev/All_in_AI/backend
python -c "from agents.basic_agent import graph; print('OK')"
```

---

## 任务 4: 更新 Docker Compose

**文件:**
- 修改: `docker-compose.yml`
- 修改: `docker-compose.dev.yml`

- [ ] **Step 1: 更新 docker-compose.yml**

```yaml
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
      context: .
      dockerfile: backend/Dockerfile.backend
    ports:
      - "2026:2026"
    env_file:
      - backend/.env
    volumes:
      - ./backend/agents:/app/agents
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

- [ ] **Step 2: 更新 docker-compose.dev.yml**

类似更新

- [ ] **Step 3: 创建 backend/Dockerfile.backend**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy workspace files
COPY agents/pyproject.toml agents/uv.lock ./agents/
COPY backend/pyproject.toml backend/uv.lock ./backend/

# Sync dependencies
RUN cd agents && uv sync
RUN cd backend && uv sync

# Copy source
COPY agents/src ./agents/src
COPY backend/agents ./backend/agents
COPY backend/.env ./backend/.env

EXPOSE 2026

CMD ["aegra", "dev"]
```

---

## 任务 5: 端到端验证

- [ ] **Step 1: 验证 agents 包导入**

```bash
cd D:/Dev/All_in_AI
conda activate langchain-next
python -c "import sys; sys.path.insert(0, 'agents/src'); from agents import create_basic_agent; print('agents OK')"
```

- [ ] **Step 2: 验证 backend Aegra**

```bash
cd D:/Dev/All_in_AI/backend
aegra dev
```

- [ ] **Step 3: 启动 frontend**

```bash
cd D:/Dev/All_in_AI/frontend
pnpm dev
```

- [ ] **Step 4: 测试 /skills 端点**

```bash
curl http://localhost:2026/skills
```

- [ ] **Step 5: 测试对话**

打开浏览器访问 http://localhost:3000

---

## 任务 6: 清理

- [ ] **Step 1: 删除备份（验证完成后）**

```bash
rm -rf D:/Dev/All_in_AI/_backup
```

- [ ] **Step 2: 提交更改**

```bash
git add -A
git commit -m "feat: restructure into agents/backend/frontend layers"
```
