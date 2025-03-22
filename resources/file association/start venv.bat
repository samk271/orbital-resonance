@echo off
cd /d "%~dp0..\..\src"
CALL ..\..\venv\Scripts\activate.bat
python main.py %1
CALL deactivate