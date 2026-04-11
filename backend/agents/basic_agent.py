"""Basic conversational agent using deepagents."""

from typing import Any

from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


def create_basic_agent(model_name: str = "gpt-4o") -> dict[str, Any]:
    """Create a deep agent using deepagents library.

    Args:
        model_name: The model to use for the agent. Use "claude-*" for Anthropic models.

    Returns:
        A dict containing the graph and metadata.
    """
    # Choose model based on name
    if "claude" in model_name.lower():
        model = ChatAnthropic(model=model_name)
    else:
        model = ChatOpenAI(model=model_name)

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
