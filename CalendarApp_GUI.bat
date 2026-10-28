@echo off
REM Calendar App Launcher - GUI Mode
REM Double-click this file to run the app without a console window.
REM For debugging (console output, errors), use CalendarApp.bat instead.

REM Run from src\ so the calendar_app package can be imported
cd /d "%~dp0src"

REM pyw.exe = Python launcher without console (same Python as py.exe in CalendarApp.bat)
start "" pyw -m calendar_app.main
