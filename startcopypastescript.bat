@echo off
setlocal
cd /d "%~dp0"
set "SCRIPT=copypaste.py"

:: Try Python launcher first
where py >nul 2>nul && (py -3 "%SCRIPT%" %* & goto :eof)

:: Fallback to python on PATH
where python >nul 2>nul && (python "%SCRIPT%" %* & goto :eof)

echo Python not found. Install Python 3 and try again.
pause
