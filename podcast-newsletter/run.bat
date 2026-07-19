@echo off
REM Windows launcher for the Podcast Digest control panel.
REM Double-click this file in File Explorer.
cd /d "%~dp0"

if not exist .venv (
  echo First-time setup - installing ^(takes a minute^)...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo --------------------------------------------------
echo   Podcast Digest is running.
echo   Open your browser to:  http://localhost:8000
echo   (Close this window to stop it.)
echo --------------------------------------------------
echo.

start "" http://localhost:8000
uvicorn app.main:app --host 127.0.0.1 --port 8000
