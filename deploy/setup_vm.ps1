<#
==============================================================================
Target VM Provisioning Script (Windows Server / Windows 10/11 VM)
Installs Chocolatey, Python, Google Chrome, and Docker Desktop
==============================================================================
#>

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Starting Windows VM Provisioning for CI/CD & Testing" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. Install Chocolatey Package Manager if not present
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "--> Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# 2. Install Git, Python, and Google Chrome
Write-Host "--> Installing Python 3.11, Git, and Google Chrome..." -ForegroundColor Yellow
choco install -y git python311 googlechrome

# 3. Refresh Environment Variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 4. Install Python test dependencies
Write-Host "--> Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "=========================================================" -ForegroundColor Green
Write-Host " Windows VM Setup Complete!" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green
