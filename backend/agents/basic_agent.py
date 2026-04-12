"""Interactive conversational agent for All_in_AI."""

import os
from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends.state import StateBackend
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
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
