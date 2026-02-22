@echo off
title Luna AI System Startup

:: --- CONFIGURATION PATHS ---
:: Please update these paths to exactly match your folders!
set PROJECT_ROOT=D:\Project_Luna
set EXTENSION_DIR=D:\Project_Luna\extension
set COMFYUI_DIR=C:\ComfyUI_windows_portable

echo ========================================
echo Launching Luna AI System...
echo ========================================

:: 1. Start ComfyUI (Runs in a new window, stays open)
echo [1/3] Starting ComfyUI...
cd /d "%COMFYUI_DIR%"
start "ComfyUI" cmd /k "run_nvidia_gpu.bat"

:: Wait 3 seconds to give the GPU a moment to initialize
timeout /t 3 /nobreak >nul

:: 2. Start FastAPI Backend (Runs in a new window, stays open)
echo [2/3] Starting Python Backend...
cd /d "%PROJECT_ROOT%"
start "Luna Backend" cmd /k "python -m poetry run uvicorn server.src.api.main:app"

:: 3. Build Chrome Extension (Runs, builds, and closes itself)
echo [3/3] Building Chrome Extension...
cd /d "%EXTENSION_DIR%"
start "Luna Extension Build" cmd /c "npm run build && echo Build complete! && timeout /t 3"

echo.
echo All systems successfully launched!
timeout /t 3 >nul