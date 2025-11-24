@echo off
REM Simple launcher without encoding issues
cd /d "%~dp0"
echo Launching Chinese Character Generator...
venv\Scripts\python.exe src\main.py
pause