@echo off
REM ============================================================================
REM Calendar App Launcher - Double-click this file to run the app
REM ============================================================================
REM 
REM This is a Windows batch file (.bat) - like a shell script in C/Unix
REM @echo off = don't show commands as they execute (cleaner output)
REM REM = comment line (like // in C)

REM Change to the application directory
REM %~dp0 = directory where this batch file is located
cd /d "%~dp0\src\calendar_app"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x and try again
    pause
    exit /b 1
)

REM Print startup message
echo Starting UK ILR Calendar App...
echo.

REM Run the Python application
REM python.exe calls the Python interpreter with our main.py file
python main.py

REM If we get here, the app has closed
echo.
echo Calendar App has closed.

REM Keep window open so user can see any error messages
echo Press any key to close this window...
pause >nul