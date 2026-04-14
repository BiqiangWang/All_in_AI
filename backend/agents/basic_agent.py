"""Aegra graph configuration for All-in-AI."""
import sys
from pathlib import Path
import importlib.util

# Resolve path to agents package
project_root = Path(__file__).parent.parent
agents_pkg_path = (project_root / ".." / "agents" / "src" / "agents").resolve()
basic_agent_file = agents_pkg_path / "basic_agent.py"

# Load the module directly without using import system
spec = importlib.util.spec_from_file_location("agents_basic_agent", basic_agent_file)
module = importlib.util.module_from_spec(spec)
sys.modules["agents_basic_agent"] = module
spec.loader.exec_module(module)

create_basic_agent = module.create_basic_agent


def get_graph():
    return create_basic_agent()["graph"]


# For Aegra loading - export get_graph as graph (Aegra will call it)
graph = get_graph
