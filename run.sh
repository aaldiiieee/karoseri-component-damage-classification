#!/bin/bash

# Function to display help
show_help() {
    echo "Usage: ./run.sh [option]"
    echo "Options:"
    echo "  --dev   Start server in development mode (with --reload)"
    echo "  --prod  Start server in production mode"
    echo "  --help  Show this help message"
}

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment (.venv) not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Default to development mode if no argument is provided
MODE=${1:-"--dev"}

case $MODE in
    --dev)
        echo "🚀 Starting server in DEVELOPMENT mode..."
        python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
        ;;
    --prod)
        echo "🚀 Starting server in PRODUCTION mode..."
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    --help)
        show_help
        ;;
    *)
        echo "Unknown option: $MODE"
        show_help
        exit 1
        ;;
esac
