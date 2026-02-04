#!/bin/bash
# Start Python FastAPI Backend for AI Calendar

cd "$(dirname "$0")/server"

echo "🚀 Starting AI Calendar API Server..."
uv run python run.py
