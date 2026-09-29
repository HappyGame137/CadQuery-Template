@echo off
setlocal
cd /d "%~dp0"
py -3.12 setup_project.py
if errorlevel 1 (
  echo.
  echo Setup failed. Read the error above. See README.md for help.
  pause
  exit /b 1
)
echo.
echo Ready. Open Design.code-workspace in VS Code.
pause
