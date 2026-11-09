@echo off
REM josspatech.com is served from GitHub Pages on the master branch (legacy),
REM while day-to-day work is on main. Push both so a main-only push cannot
REM leave the live site stuck on an old snapshot again.
setlocal
cd /d "%~dp0.."
git push origin main
if errorlevel 1 exit /b 1
git push origin main:master
if errorlevel 1 exit /b 1
echo Published main and synced master for Pages.
endlocal
