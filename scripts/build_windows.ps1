$ErrorActionPreference = "Stop"

$Root = Resolve-Path "$PSScriptRoot\.."
Set-Location $Root

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name "Mindful-Monk" `
    --add-data "app/assets;assets" `
    mindful_monk.py

Write-Host "Built: $Root\dist\Mindful-Monk.exe"
