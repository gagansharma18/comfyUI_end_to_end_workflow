@echo off
setlocal
title ComfyUI Cinematic AI Film Generator

echo ==============================================================
echo 🎬 CINEMATIC AI FILM GENERATOR - PIPELINE RUNNER 🎬
echo ==============================================================
echo.
echo This script will read your cinematic script, generate each scene
echo sequentially inside ComfyUI, animate the transitions between scenes
echo using Wan 2.2 Image-to-Video, download the resulting clips, and
echo stitch them together into a final combined movie.
echo.
echo Make sure ComfyUI is running in the background at http://127.0.0.1:8188.
echo.

:: Detect ComfyUI Virtual Environment Python
set PYTHON_EXE="C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe"

if not exist %PYTHON_EXE% (
    echo.
    echo [ERROR] ComfyUI Virtual Environment Python not found at:
    echo %PYTHON_EXE%
    echo Please make sure ComfyUI is installed correctly.
    echo.
    pause
    exit /b 1
)

:: Ask user for script path, defaulting to input\cinematic_script.md
set SCRIPT_PATH=input\cinematic_script.md
set /p USER_INPUT="Enter path to your cinematic script file [default: input\cinematic_script.md]: "
if not "%USER_INPUT%"=="" set SCRIPT_PATH=%USER_INPUT%

if not exist "%SCRIPT_PATH%" (
    echo.
    echo [ERROR] Cinematic script file "%SCRIPT_PATH%" not found!
    echo Please check the filename and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo Running cinematic generation using: %SCRIPT_PATH%
echo --------------------------------------------------------------
echo.

%PYTHON_EXE% scripts\run_pipeline.py "%SCRIPT_PATH%"

echo.
echo ==============================================================
echo Done! Your final merged cinematic video file has been saved to:
echo   output\final_storyboard.mp4
echo ==============================================================
echo.
pause
