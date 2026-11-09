@echo off
REM Live site publishes from GitHub Actions on main (see .github/workflows/pages.yml).
REM master is kept in sync for the legacy branch mirror only ? do not trigger a second
REM Pages workflow from master (that raced main and timed out the large artifact).
setlocal
cd /d "%~dp0.."
git push origin main
if errorlevel 1 exit /b 1
git push origin main:master
if errorlevel 1 exit /b 1
echo Published main (Actions Pages) and synced master mirror.
endlocal
