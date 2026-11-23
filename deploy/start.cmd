@echo off
setlocal
cd /d "%~dp0"
if not exist "runtime\python\pythonw.exe" (
    echo Extract the entire ZIP before running this file.
    pause
    exit /b 1
)
start "" "runtime\python\pythonw.exe" -E -s "tools\launch.py"
