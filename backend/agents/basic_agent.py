"""Basic conversational agent using deepagents."""

import os
from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic

# Load .env file
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)


def create_basic_agent(model_name: str = "MiniMax-M2.7") -> dict[str, Any]:
    """Create a deep agent using deepagents library.

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

    # Create deep agent using deepagents
    graph = create_deep_agent(model=model, tools=[])

    return {
        "graph": graph,
        "name": "basic-agent",
        "description": "A basic conversational agent powered by deepagents",
    }


# For Aegra loading, export graph
def get_graph() -> Any:
    """Factory function for Aegra to load the graph."""
    agent = create_basic_agent()
    return agent["graph"]


# Export graph (for static loading)
graph = get_graph()
