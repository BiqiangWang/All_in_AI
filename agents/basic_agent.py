"""All-in-AI Agent - Aegra graph entry point."""
import sys
from pathlib import Path

# Add project root to path so 'agents' package can be imported
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.core.agent import create_basic_agent, get_skills_metadata


def get_graph():
    return create_basic_agent()["graph"]


# For Aegra loading - export get_graph as graph (Aegra will call it)
graph = get_graph
