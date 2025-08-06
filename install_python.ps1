# install_python.ps1 - Python Auto-Installer
# This script downloads and installs Python automatically

Write-Host "[*] Python Auto-Installer" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Use latest stable Python 3.12 version
$PythonVersion = "3.12.7"
$PythonInstallerUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
$InstallerPath = "$env:TEMP\python-installer.exe"

try {
    Write-Host "[*] Checking internet connectivity..." -ForegroundColor Yellow
    
    # Test internet connectivity
    $testConnection = Test-NetConnection -ComputerName "www.python.org" -Port 443 -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $testConnection) {
        Write-Host "[-] No internet connection available. Cannot download Python." -ForegroundColor Red
        Write-Host "[-] Please install Python manually from https://www.python.org" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[*] Downloading Python $PythonVersion..." -ForegroundColor Yellow
    Write-Host "[*] URL: $PythonInstallerUrl" -ForegroundColor Gray
    
    # Download with progress and error handling
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($PythonInstallerUrl, $InstallerPath)
    
    if (-not (Test-Path $InstallerPath)) {
        Write-Host "[-] Download failed - installer not found at $InstallerPath" -ForegroundColor Red
        exit 1
    }
    
    $fileSize = (Get-Item $InstallerPath).Length / 1MB
    Write-Host "[+] Download completed successfully ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
    
    Write-Host "[*] Installing Python (this may take a few minutes)..." -ForegroundColor Yellow
    Write-Host "[*] Installation is running silently in the background..." -ForegroundColor Gray
    
    # Install Python with comprehensive options
    $installArgs = @(
        "/quiet"
        "InstallAllUsers=1"
        "PrependPath=1"
        "Include_test=0"
        "Include_tcltk=1"
        "Include_launcher=1"
        "AssociateFiles=1"
    )
    
    $process = Start-Process -FilePath $InstallerPath -ArgumentList $installArgs -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "[+] Python installation completed successfully!" -ForegroundColor Green
        Write-Host "[*] Python has been added to system PATH" -ForegroundColor Green
    } else {
        Write-Host "[-] Python installation failed with exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host "[-] Please try installing Python manually" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "[-] Error during Python installation: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[-] Please try installing Python manually from https://www.python.org" -ForegroundColor Red
    exit 1
} finally {
    # Clean up installer file
    if (Test-Path $InstallerPath) {
        Write-Host "[*] Cleaning up installer file..." -ForegroundColor Gray
        Remove-Item $InstallerPath -Force
    }
}

Write-Host "[*] Installation process completed." -ForegroundColor Cyan
