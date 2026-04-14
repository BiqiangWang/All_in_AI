# 项目结构调整计划

> **目标：** 简化目录结构，统一为 agents/，删除 backend/agents/

**变更说明：**
1. `agents/` 同时作为 Python 包和 Aegra 配置目录
2. 删除 `backend/agents/` 目录
3. 仅在 Docker 中启动 PostgreSQL，前后端本地启动

---

## 目标目录结构

```
D:\Dev\All_in_AI\
├── agents/                          # 同时作为 Python 包和 Aegra 配置
│   ├── pyproject.toml
│   ├── basic_agent.py               # Aegra graph 入口
│   ├── aegra.json                  # Aegra 配置
│   ├── tools/
│   ├── memory/
│   ├── skills/
│   └── prompt/
├── backend/                         # Aegra API 服务（仅 libs/）
│   ├── libs/
│   ├── .env
│   └── pyproject.toml
├── frontend/
└── docker-compose.yml              # 仅 PostgreSQL
```

---

## 任务 1: 创建 agents/aegra.json

**文件:**
- 创建: `agents/aegra.json`

- [ ] **Step 1: 创建 agents/aegra.json**

```json
{
  "graphs": {
    "all-in-ai": "./basic_agent.py:graph"
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

---

## 任务 2: 更新 agents/basic_agent.py

**文件:**
- 修改: `agents/basic_agent.py`

- [ ] **Step 1: 更新 agents/basic_agent.py**

确保导出 `graph` 变量供 Aegra 加载：

```python
"""All-in-AI Agent - Aegra graph entry point."""
import sys
from pathlib import Path

# Add agents package to path for imports
_agents_dir = Path(__file__).parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from basic_agent import create_basic_agent, get_skills_metadata


def get_graph():
    return create_basic_agent()["graph"]


# For Aegra loading - export get_graph as graph (Aegra will call it)
graph = get_graph
```

---

## 任务 3: 重构 agents/basic_agent.py 为入口文件

**文件:**
- 修改: `agents/basic_agent.py`（拆分主逻辑）

- [ ] **Step 1: 更新 agents/basic_agent.py**

现在 `agents/basic_agent.py` 作为 Aegra 入口点，需要：
1. 设置 sys.path
2. 导入 create_basic_agent
3. 导出 graph 函数

实际 agent 逻辑在 `agents/core/agent.py` 中（需要创建）

- [ ] **Step 2: 创建 agents/core/agent.py**

```python
"""Core agent creation logic."""
import os
from datetime import date
from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langchain_anthropic import ChatAnthropic

from agents.tools.memory import memory
from agents.tools.search_web import search_web


def _get_memory_context() -> str:
    """获取记忆上下文."""
    from agents.memory.memory_manager import MemoryManager
    from agents.memory.file_provider import FileMemoryProvider

    manager = MemoryManager()
    manager.add_provider(FileMemoryProvider())
    return manager.get_snapshot()


def create_basic_agent(model_name: str = "MiniMax-M2.7") -> dict[str, Any]:
    """Create an interactive conversational agent."""
    # Configure MiniMax Anthropic-compatible API
    if "ANTHROPIC_BASE_URL" not in os.environ:
        os.environ["ANTHROPIC_BASE_URL"] = "https://api.minimaxi.com/anthropic"

    model = ChatAnthropic(
        model=model_name,
        api_key=os.environ.get("MINIMAX_API_KEY"),
        base_url="https://api.minimaxi.com/anthropic",
    )

    # Build memory context
    memory_context = _get_memory_context()
    memory_instruction = f"\n## 记忆上下文\n{memory_context}\n" if memory_context else ""

    # System prompt
    system_prompt = f"""You are All_in_AI, a helpful, friendly AI assistant.
Current date: {date.today().isoformat()}
{memory_instruction}

## 回答风格
- 简洁直接，不需要废话
- 复杂问题用类比和例子解释
- 不确定就说不知道，不要编造
- 主动搜索确认不确定的事实

## 能力范围
- 回答各领域问题
- 网络搜索获取实时信息
- 帮助写作、头脑风暴
- 解释复杂概念
- 提供建议和思考框架

## 限制
- 不确定的事实主动去搜索确认
- 复杂问题先问清楚再答
- 搜索只用一次，不要重复搜索同一问题
"""

    # Skills root directory
    skills_root = Path(__file__).parent / "skills"

    # Use FilesystemBackend for skill loading
    backend = FilesystemBackend(root_dir=str(skills_root), virtual_mode=True)

    graph = create_deep_agent(
        model=model,
        tools=[search_web, memory],
        system_prompt=system_prompt,
        backend=backend,
        skills=["/nuwa/", "/elon-musk/", "/trump/", "/zhangxuefeng/"],
    )

    return {
        "graph": graph,
        "name": "all-in-ai",
        "description": "An interactive conversational agent",
    }


def get_skills_metadata() -> list[dict]:
    """扫描 skills 目录，返回 skill 元数据列表."""
    import re

    skills_root = Path(__file__).parent / "skills"
    if not skills_root.exists():
        return []

    skills = []
    for skill_dir in skills_root.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding='utf-8')
        name = skill_dir.name
        description = ""

        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            description = heading_match.group(1).strip()

        skills.append({
            "name": name,
            "description": description,
            "triggers": [],
            "path": f"/{skill_dir.name}/"
        })

    return skills
```

---

## 任务 4: 删除 backend/agents/

**文件:**
- 删除: `backend/agents/` 整个目录

- [ ] **Step 1: 删除 backend/agents/**

```bash
rm -rf D:/Dev/All_in_AI/backend/agents
```

---

## 任务 5: 更新 backend/pyproject.toml

**文件:**
- 修改: `backend/pyproject.toml`

- [ ] **Step 1: 更新 backend/pyproject.toml**

```toml
[project]
name = "aegra-workspace"
version = "0.0.0"
requires-python = ">=3.12"
dependencies = [
    "agents",
]

[tool.uv]
package = false

[tool.uv.workspace]
members = ["libs/*", "../agents"]
```

---

## 任务 6: 简化 docker-compose.yml

**文件:**
- 修改: `docker-compose.yml`

- [ ] **Step 1: 简化 docker-compose.yml（仅 PostgreSQL）**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: aegra-postgres
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

volumes:
  postgres_data:
```

- [ ] **Step 2: 删除 docker-compose.dev.yml**

```bash
rm D:/Dev/All_in_AI/docker-compose.dev.yml
```

---

## 任务 7: 验证

- [ ] **Step 1: 启动 PostgreSQL**

```bash
cd D:/Dev/All_in_AI
docker compose up -d postgres
```

- [ ] **Step 2: 验证 agents 导入**

```bash
cd D:/Dev/All_in_AI
conda activate langchain-next
python -c "import sys; sys.path.insert(0, 'agents'); from agents.core.agent import create_basic_agent; print('OK')"
```

- [ ] **Step 3: 启动 Aegra**

```bash
cd D:/Dev/All_in_AI/agents
aegra dev
```

- [ ] **Step 4: 验证 health**

```bash
curl http://localhost:2026/health
```

---

## 任务 8: 提交

- [ ] **Step 1: 提交更改**

```bash
git add -A
git commit -m "refactor: unify agents/ and remove backend/agents/"
```
