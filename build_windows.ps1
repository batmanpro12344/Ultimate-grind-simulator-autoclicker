$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
py -3 -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
py -3 -m PyInstaller --noconfirm --clean --windowed --onedir --name UltimateGrindAutoClicker --collect-submodules pynput app.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
$iscc = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "${env:ProgramFiles}\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw 'Install Inno Setup 6 (https://jrsoftware.org/isinfo.php), then rerun this script.' }
& $iscc installer.iss
if ($LASTEXITCODE -ne 0) { throw 'Installer build failed' }
Write-Host 'Installer available in release\' -ForegroundColor Green
