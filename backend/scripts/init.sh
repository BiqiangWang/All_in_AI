#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Creating Python virtual environment..."
python -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install deepagents aegra-api
pip install -e ./deepagents 2>/dev/null || true

echo "Installing additional dependencies..."
pip install langgraph langchain-openai python-dotenv asyncpg

echo "Setup complete!"
echo "Run 'source .venv/bin/activate' to activate the environment"
