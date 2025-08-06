@echo off
setlocal enabledelayedexpansion

echo Windows Update Disabler - Launcher
echo ===================================

:: Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Python not found, attempting to install...
    
    :: Check if PowerShell script exists
    if not exist "install_python.ps1" (
        echo [-] Error: install_python.ps1 not found in script directory.
        echo [-] Please install Python manually or ensure all files are present.
        pause
        exit /b 1
    )
    
    :: Run PowerShell installation script
    powershell -ExecutionPolicy Bypass -File "install_python.ps1"
    
    :: Check if Python installation was successful
    where python >nul 2>nul
    if !errorlevel! neq 0 (
        echo [-] Python installation failed or Python is not in PATH.
        echo [-] Please install Python manually and try again.
        pause
        exit /b 1
    )
    
    echo [+] Python installation completed.
) else (
    echo [+] Python is already installed.
)

:: Check if the main Python script exists
if not exist "disable_windows_update.py" (
    echo [-] Error: disable_windows_update.py not found in script directory.
    echo [-] Please ensure all files are present.
    pause
    exit /b 1
)

:: Run the main Python script as Administrator
echo [*] Launching Windows Update disabler with administrator privileges...
echo [*] Please accept the UAC prompt if it appears...

powershell -Command "Start-Process python -ArgumentList '%SCRIPT_DIR%disable_windows_update.py' -Verb RunAs -Wait"

if %errorlevel% equ 0 (
    echo [+] Script execution completed.
) else (
    echo [-] Script execution may have failed or was cancelled.
)

echo.
echo Press any key to exit...
pause >nul
endlocal
