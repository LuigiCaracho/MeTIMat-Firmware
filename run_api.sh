#!/usr/bin/env bash

# Get the script's absolute directory to avoid path issues
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# Start the backend in the foreground
echo "Starting backend..."
"$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/mock_server.py"
