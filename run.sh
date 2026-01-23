#!/usr/bin/env bash

# Get the script's absolute directory to avoid path issues
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# Ensure the Display environment variable is set (required for GUI on Pi)
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
fi

echo "🚀 Starting MeTIMat Machine Interface from $SCRIPT_DIR..."
echo "📅 Date: $(date)"

# Use absolute path to the virtual environment python
PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Error: Virtual environment python not found at $PYTHON_BIN"
    exit 1
fi

# Start the beep listener in the user context (as the current user)
# This handles audio playback since root often doesn't have access to the user's audio session.
"$PYTHON_BIN" "$SCRIPT_DIR/beep_listener.py" &
BEEP_PID=$!

# Run the main script as root (required for LED DMA)
sudo "$PYTHON_BIN" "$SCRIPT_DIR/main.py"

# Clean up the beep listener when the main script exits
kill $BEEP_PID
