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
