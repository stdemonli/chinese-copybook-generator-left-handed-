@echo off
cd /d "%~dp0"
REM Silent launcher using pythonw
start "" "venv\Scripts\pythonw.exe" "src\main.py"
exit