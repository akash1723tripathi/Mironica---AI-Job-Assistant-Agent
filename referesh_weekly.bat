@echo off
cd /d "D:\codes\Projects\AI Job Assistant"

call .venv\Scripts\activate.bat

python src\registry\build_registry.py

exit