#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Creating Python virtual environment..."
python -m venv .venv

echo "Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
fi

echo "Installing dependencies..."
pip install deepagents aegra-api
if [ -d "./deepagents" ]; then
    pip install -e ./deepagents
fi

echo "Installing additional dependencies..."
pip install langgraph langchain-openai python-dotenv asyncpg

echo "Setup complete!"
echo "Run 'source .venv/bin/activate' to activate the environment"
