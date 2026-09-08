@REM @echo off
@REM cd /d "%~dp0"
@REM .\python_env\python.exe .\scripts\gui-admin.py
@REM pause






@echo off
set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"

:: Point directly to your folder named "python"
set "PYTHON_PATH=%APP_DIR%\python_env\python"

if not exist "%PYTHON_PATH%\python.exe" (
    echo ERROR: Cannot find python.exe inside the engine folder!
    echo Looked here: "%PYTHON_PATH%\python.exe"
    pause
    exit
)

:: Launch the Tkinter desktop script using the engine
start "" "%PYTHON_PATH%\pythonw.exe" "%APP_DIR%\scripts\gui-admin.py"
exit

