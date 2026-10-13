param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& $Python -m pip install -r requirements.txt
& $Python -m PyInstaller --noconfirm FormulaSnip.spec
if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
