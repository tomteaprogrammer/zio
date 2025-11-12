@echo off
setlocal
cd /d "%~dp0"
set "SCRIPT=copypaste.py"

:: Always open a visible console and keep it open after running
if exist "%SystemRoot%\py.exe" (
  cmd /k py -3 "%SCRIPT%" --enable
) else if exist "%SystemRoot%\System32\python.exe" (
  cmd /k python "%SCRIPT%" --enable
) else (
  echo Python not found. Install Python 3 from python.org and try again.
  pause
)
