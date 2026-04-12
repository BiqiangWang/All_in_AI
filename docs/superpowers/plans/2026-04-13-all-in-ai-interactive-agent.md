# All_in_AI Interactive Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform All_in_AI into a minimal interactive conversational agent with only `search_web` tool and clean system prompt. Remove all code-development tools.

**Architecture:** Refactor `basic_agent.py` to use MiniMax-M2.7 via Anthropic-compatible API, add only `search_web` tool, and use a concise system prompt defining the agent's personality and capabilities.

**Tech Stack:** deepagents 0.4.4, MiniMax-M2.7 (Anthropic-compatible), langchain-anthropic, Python 3.12

---

## File Structure

```
backend/
├── agents/
│   └── basic_agent.py          # [MODIFY] Remove FS tools, add search_web, concise system prompt
├── .env                       # [EXISTING] MINIMAX_API_KEY already set
└── aegra.json                 # [MODIFY] Rename assistant to "all-in-ai"

frontend/
└── .env.local                 # [MODIFY] Update NEXT_PUBLIC_ASSISTANT_ID=all-in-ai
```

---

## Task 1: Refactor `basic_agent.py`

**Files:**
- Modify: `backend/agents/basic_agent.py`

### Step 1: Read current `basic_agent.py`

```bash
cat D:/Dev/All_in_AI/backend/agents/basic_agent.py
```

### Step 2: Write new `basic_agent.py`

```python
"""Interactive conversational agent for All_in_AI."""

import os
from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends.state import StateBackend
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from pydantic import Field

# Load .env file
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)


@tool
def search_web(query: str = Field(description="The search query to look up on the web")) -> str:
    """Search the web for information about a topic or question.

    Use this when you need to find current information, facts, news, or answers
    that require looking up on the internet.

    Args:
        query: The search query to look up

    Returns:
        Search results with titles and snippets
    """
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

    search = DuckDuckGoSearchAPIWrapper()
    try:
        results = search.run(query)
        return results if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


def create_basic_agent(model_name: str = "MiniMax-M2.7") -> dict[str, Any]:
    """Create an interactive conversational agent.

    Args:
        model_name: The model to use. Defaults to "MiniMax-M2.7".

    Returns:
        A dict containing the graph and metadata.
    """
    # Configure MiniMax Anthropic-compatible API
    os.environ["ANTHROPIC_BASE_URL"] = "https://api.minimaxi.com/anthropic"

    model = ChatAnthropic(
        model=model_name,
        api_key=os.environ.get("MINIMAX_API_KEY"),
        base_url="https://api.minimaxi.com/anthropic",
    )

    # Concise system prompt for conversational agent
    system_prompt = """You are All_in_AI, a helpful, friendly AI assistant.

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
"""

    graph = create_deep_agent(
        model=model,
        tools=[search_web],
        system_prompt=system_prompt,
        backend=StateBackend,
    )

    return {
        "graph": graph,
        "name": "all-in-ai",
        "description": "An interactive conversational agent",
    }


# For Aegra loading
def get_graph() -> Any:
    """Factory function for Aegra to load the graph."""
    agent = create_basic_agent()
    return agent["graph"]


# Export graph (for static loading)
graph = get_graph()
```

### Step 3: Verify imports

```bash
cd D:/Dev/All_in_AI/backend
python -c "from agents.basic_agent import create_basic_agent; print('OK')"
```

### Step 4: Commit

```bash
git add backend/agents/basic_agent.py
git commit -m "refactor: simplify to conversational agent with search_web only"
```

---

## Task 2: Update `aegra.json`

**Files:**
- Modify: `backend/aegra.json`

### Step 1: Read current `aegra.json`

```bash
cat D:/Dev/All_in_AI/backend/aegra.json
```

### Step 2: Update `aegra.json`

```json
{
  "$schema": "https://docs.aegra.dev/schema.json",
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
  },
  "store": {
    "enabled": false
  },
  "observability": {
    "enabled": false
  }
}
```

### Step 3: Commit

```bash
git add backend/aegra.json
git commit -m "feat: rename agent to 'all-in-ai' in aegra.json"
```

---

## Task 3: Update frontend `.env.local`

**Files:**
- Modify: `frontend/.env.local`

### Step 1: Read current `.env.local`

```bash
cat D:/Dev/All_in_AI/frontend/.env.local
```

### Step 2: Update

```
NEXT_PUBLIC_API_URL=http://localhost:2026
NEXT_PUBLIC_ASSISTANT_ID=all-in-ai
```

### Step 3: Commit

```bash
git add frontend/.env.local
git commit -m "feat: update frontend ASSISTANT_ID to 'all-in-ai'"
```

---

## Task 4: Verify end-to-end

### Step 1: Restart backend

```bash
# Kill existing backend
netstat -ano | grep 2026
# taskkill //F //PID <PID>

# Start new backend
cd D:/Dev/All_in_AI/backend
C:/Software/anaconda3/envs/langchain-next/python.exe start_aegra_v2.py
```

### Step 2: Test health

```bash
curl http://localhost:2026/health
```

Expected: `{"status":"healthy",...}`

### Step 3: Test assistant

```bash
curl http://localhost:2026/assistants
```

Expected: should list `all-in-ai` assistant

### Step 4: Test a conversation

```bash
THREAD_ID=$(curl -s -X POST http://localhost:2026/threads \
  -H "Content-Type: application/json" \
  -d '{"assistant_id":"all-in-ai"}' | python -c "import sys,json; print(json.load(sys.stdin)['thread_id'])")

curl -s -X POST "http://localhost:2026/threads/$THREAD_ID/runs" \
  -H "Content-Type: application/json" \
  -d '{"assistant_id":"all-in-ai","mode":{"type":"single","single":{}},"input":{"messages":[{"role":"user","content":"Hello, who are you?"}]}}' \
  --max-time 60
```

Wait for status=success, then check response content.

### Step 5: Final status

```bash
git status
git log --oneline -5
```

---

## Dependencies

```
Task 1 ──┬── Task 4 (verify)
Task 2 ──┤
Task 3 ──┘
```
