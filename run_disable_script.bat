@echo off
setlocal enabledelayedexpansion

:: Check for command line arguments
set "SCRIPT_ARGS="
set "VERBOSE_MODE=false"

:: Parse all command line arguments
:parse_args
if "%1"=="" goto :args_done
if "%1"=="--rollback" set "SCRIPT_ARGS=%SCRIPT_ARGS% --rollback"
if "%1"=="--validate" set "SCRIPT_ARGS=%SCRIPT_ARGS% --validate"
if "%1"=="--verbose" (
    set "SCRIPT_ARGS=%SCRIPT_ARGS% --verbose"
    set "VERBOSE_MODE=true"
)
if "%1"=="-v" (
    set "SCRIPT_ARGS=%SCRIPT_ARGS% --verbose"
    set "VERBOSE_MODE=true"
)
if "%1"=="-h" set "SCRIPT_ARGS=%SCRIPT_ARGS% --help"
if "%1"=="--help" set "SCRIPT_ARGS=%SCRIPT_ARGS% --help"
shift
goto :parse_args
:args_done

:: Display appropriate header based on arguments
echo Windows Update Disabler - Launcher
if "%SCRIPT_ARGS%" NEQ "" (
    echo Arguments: %SCRIPT_ARGS%
)
if "%VERBOSE_MODE%"=="true" (
    echo [VERBOSE MODE ENABLED - Detailed logging will be shown]
)
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
echo [*] Launching with administrator privileges...
if "%VERBOSE_MODE%"=="true" (
    echo [*] Verbose logging is enabled - detailed output will be shown
    echo [*] Log files will be saved in the 'logs' directory
)
echo [*] Please accept the UAC prompt if it appears...

if "%SCRIPT_ARGS%"=="" (
    powershell -Command "Start-Process python -ArgumentList '%SCRIPT_DIR%disable_windows_update.py' -Verb RunAs -Wait"
) else (
    powershell -Command "Start-Process python -ArgumentList '%SCRIPT_DIR%disable_windows_update.py%SCRIPT_ARGS%' -Verb RunAs -Wait"
)

if %errorlevel% equ 0 (
    echo [+] Script execution completed.
) else (
    echo [-] Script execution may have failed or was cancelled.
)

echo.
echo Press any key to exit...
pause >nul
endlocal
