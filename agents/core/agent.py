"""Core agent creation logic."""
import os
from datetime import date
from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from pydantic import Field


# Lazy-loaded memory provider
_memory_provider = None


def _get_memory_provider():
    """Lazy initialization of memory provider."""
    global _memory_provider
    if _memory_provider is None:
        from agents.memory.file_provider import FileMemoryProvider
        _memory_provider = FileMemoryProvider()
    return _memory_provider


# Skills root directory
skills_root = Path(__file__).parent.parent / "skills"


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
    from ddgs import DDGS

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No results found."
            formatted = []
            for r in results:
                title = r.get("title", "").strip()
                body = r.get("body", "").strip()
                if title and body:
                    formatted.append(f"{title}\n{body}")
            return "\n\n".join(formatted) if formatted else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def memory(target: str = Field(description="'agent' for agent's own memory, 'user' for user profile"),
           action: str = Field(description="'read' to retrieve memory, 'update' to modify existing section"),
           content: str = Field(default=None, description="Content to store in the specified section."),
           section: str = Field(default=None, description="Which section to update (e.g., '设定', '已知事实', '基础信息').")) -> str:
    """Read from or update memory store.

    Examples:
    - Read memory: memory(target="agent", action="read")
    - Update memory: memory(target="agent", action="update", section="已知事实", content="用户称呼为小汪")
    - Update profile: memory(target="user", action="update", section="基础信息", content="- 称呼：小汪")
    """
    args = {"target": target, "action": action, "content": content}
    if section:
        args["section"] = section
    return _get_memory_provider().handle_tool_call("memory", args)


def _get_memory_context() -> str:
    """获取记忆上下文，被 memory 工具调用和 system prompt 注入共享"""
    from agents.memory.memory_manager import MemoryManager
    from agents.memory.file_provider import FileMemoryProvider

    manager = MemoryManager()
    manager.add_provider(FileMemoryProvider())
    return manager.get_snapshot()


def create_basic_agent(model_name: str = "MiniMax-M2.7") -> dict[str, Any]:
    """Create an interactive conversational agent.

    Args:
        model_name: The model to use. Defaults to "MiniMax-M2.7".

    Returns:
        A dict containing the graph and metadata.
    """
    # Configure MiniMax Anthropic-compatible API
    if "ANTHROPIC_BASE_URL" not in os.environ:
        os.environ["ANTHROPIC_BASE_URL"] = "https://api.minimaxi.com/anthropic"

    model = ChatAnthropic(
        model=model_name,
        api_key=os.environ.get("MINIMAX_API_KEY"),
        base_url="https://api.minimaxi.com/anthropic",
    )

    # Build memory context for injection into system prompt
    memory_context = _get_memory_context()

    # Format memory instructions for the agent
    memory_instruction = ""
    if memory_context:
        memory_instruction = f"""
## 记忆
{memory_context}

[When user shares information about themselves, use the memory tool to store it naturally.]
"""

    # Concise system prompt for conversational agent
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
    """扫描 skills 目录，返回 skill 元数据列表"""
    import re

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

        # Parse frontmatter
        name = skill_dir.name
        description = ""
        triggers = []

        # Extract from first markdown heading as fallback
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            description = heading_match.group(1).strip()

        # Extract name from frontmatter if present
        fm_name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if fm_name_match:
            name = fm_name_match.group(1).strip()

        skills.append({
            "name": name,
            "description": description,
            "triggers": triggers,
            "path": f"/{skill_dir.name}/"
        })

    return skills
