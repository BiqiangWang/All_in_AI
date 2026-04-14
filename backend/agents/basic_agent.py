"""Interactive conversational agent for All_in_AI."""

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
        from backend.memory.file_provider import FileMemoryProvider
        _memory_provider = FileMemoryProvider()
    return _memory_provider

# Load .env file
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)

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
            # Format results cleanly
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
def memory(target: str = Field(description="Target store: 'agent' for agent memory, 'user' for user profile"),
           action: str = Field(description="Action to perform: read, add, replace, or remove"),
           content: str = Field(default=None, description="Content to add or replace"),
           old_text: str = Field(default=None, description="Old text to replace (for replace/remove actions)")) -> str:
    """Read from or write to memory store.

    Use this tool to store and retrieve persistent information that the agent
    should remember across conversations, such as user preferences, facts,
    or important context. The target parameter specifies which store to use.

    Targets:
    - agent: Agent memory - stores agent's own knowledge and context
    - user: User profile - stores user preferences and context

    Actions:
    - read: Retrieve all current memory content
    - add: Append new content to memory
    - replace: Replace specific old text with new content
    - remove: Remove specific text from memory
    """
    return _get_memory_provider().handle_tool_call("memory", {
        "target": target,
        "action": action,
        "content": content,
        "old_text": old_text,
    })


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

    # Concise system prompt for conversational agent
    system_prompt = f"""You are All_in_AI, a helpful, friendly AI assistant.
Current date: {date.today().isoformat()}

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


# For Aegra loading
def get_graph() -> Any:
    """Factory function for Aegra to load the graph."""
    agent = create_basic_agent()
    return agent["graph"]


# Export graph (for static loading)
graph = get_graph()


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


def extract_skill_names(text: str) -> list[str]:
    """从文本中提取 /skillname 格式的命令"""
    import re
    matches = re.findall(r'/([a-zA-Z0-9_-]+)', text)
    return matches


def load_skill_content(skill_name: str) -> str:
    """加载指定 skill 的 SKILL.md 内容"""
    skill_path = skills_root / skill_name / "SKILL.md"
    if skill_path.exists():
        return skill_path.read_text(encoding='utf-8')
    return ""


def activate_skills_in_message(message: str, system_prompt: str) -> str:
    """检测消息中的 skill 命令并激活对应的 skill 内容"""
    skill_names = extract_skill_names(message)
    if not skill_names:
        return system_prompt

    activated_content = []
    for skill_name in skill_names:
        content = load_skill_content(skill_name)
        if content:
            activated_content.append(content)

    if activated_content:
        return "\n\n".join(activated_content) + "\n\n" + system_prompt
    return system_prompt
