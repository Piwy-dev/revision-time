#!/bin/bash

# Study Tracker - Startup Script

echo "🚀 Starting Study Tracker..."
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv sync
fi

echo "📚 Starting Backend (FastAPI + SQLite)..."
echo "   Backend runs on http://localhost:8000"
echo ""

# Start the backend
.venv/bin/python -m backend.main
