#!/bin/bash

# Clear terminal and set title
clear
echo "=============================================================="
echo "🎬 STIXX STORIES - FULL MOVIE GENERATOR (macOS) 🎬"
echo "=============================================================="
echo ""
echo "This script will read your story script, generate each scene"
echo "sequentially inside ComfyUI, download the images and video clips,"
echo "and stitch them together into a single combined movie."
echo ""
echo "Make sure ComfyUI is running in the background at http://127.0.0.1:8188."
echo ""

# Detect ComfyUI Virtual Environment Python on macOS
# Common Comfy-Desktop locations on macOS:
COMFY_VENV_1="$HOME/Library/Application Support/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/bin/python"
COMFY_VENV_2="$HOME/Library/Application Support/Comfy-Desktop/ComfyUI/.venv/bin/python"
LOCAL_VENV="./.venv/bin/python"

PYTHON_EXE=""

if [ -f "$COMFY_VENV_1" ]; then
    PYTHON_EXE="$COMFY_VENV_1"
elif [ -f "$COMFY_VENV_2" ]; then
    PYTHON_EXE="$COMFY_VENV_2"
elif [ -f "$LOCAL_VENV" ]; then
    PYTHON_EXE="$LOCAL_VENV"
else
    # Fallback to system python3 if venv is not found
    if command -v python3 &>/dev/null; then
        PYTHON_EXE="python3"
    else
        echo "[ERROR] Python 3 could not be found."
        echo "Please make sure Python 3 is installed."
        exit 1
    fi
fi

echo "Using Python: $PYTHON_EXE"
echo ""

# Ask user for script path, defaulting to input/episode_2.md
SCRIPT_PATH="input/episode_2.md"
read -p "Enter path to your story script file [default: input/episode_2.md]: " USER_INPUT

if [ ! -z "$USER_INPUT" ]; then
    SCRIPT_PATH="$USER_INPUT"
fi

if [ ! -f "$SCRIPT_PATH" ]; then
    echo ""
    echo "[ERROR] Story script file \"$SCRIPT_PATH\" not found!"
    echo "Please check the filename and try again."
    echo ""
    exit 1
fi

echo ""
echo "Running generation using: $SCRIPT_PATH"
echo "--------------------------------------------------------------"
echo ""

"$PYTHON_EXE" scripts/run_pipeline.py "$SCRIPT_PATH"

echo ""
echo "=============================================================="
echo "Done! Your final merged video file has been saved to:"
echo "  output/final_storyboard.mp4"
echo "=============================================================="
echo ""
