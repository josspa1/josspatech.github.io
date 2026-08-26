@echo off
REM PocketBudJet partner showcase — local preview (narration + locales)
cd /d "%~dp0"
echo.
echo   Partner showcase at http://127.0.0.1:8765/
echo   Press Ctrl+C to stop the server.
echo.
start "" "http://127.0.0.1:8765/"
python -m http.server 8765 --bind 127.0.0.1
