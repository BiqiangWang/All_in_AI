"""All-in-AI Agent - Aegra graph entry point."""
import sys
from pathlib import Path

# Add agents package to path for imports
_agents_dir = Path(__file__).parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from core.agent import create_basic_agent, get_skills_metadata


def get_graph():
    return create_basic_agent()["graph"]


# For Aegra loading - export get_graph as graph (Aegra will call it)
graph = get_graph
