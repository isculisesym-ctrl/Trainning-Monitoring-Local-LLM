@echo off
REM 12-Hour Training Script Launcher

echo.
echo ================================================================================
echo                    AI PLATFORM - 12 HOUR TRAINING
echo ================================================================================
echo.
echo Training your Sr-level model for 12 hours continuously.
echo.
echo Checking Ollama...
curl -s http://localhost:11434/api/tags > nul 2>&1

if %errorlevel% equ 0 (
    echo ? Ollama is running
    echo.
    echo Training in progress... (logs to data/training_logs/)
    echo.
    python training_12h.py
) else (
    echo ? Ollama is NOT running!
    echo.
    echo Start Ollama first:
    echo   ollama serve
    echo.
    pause
)
