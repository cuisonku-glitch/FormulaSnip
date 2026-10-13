param(
    [string]$Python = 'python',
    [switch]$SkipInstall
)
$ErrorActionPreference = 'Stop'
$PythonCommand = (Get-Command $Python -ErrorAction Stop).Source
Push-Location $PSScriptRoot
try {
    if (-not $SkipInstall) {
        & $PythonCommand -m pip install -r FormulaSnip/requirements-lock.txt
        if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    }
    & $PythonCommand download_assets.py
    if ($LASTEXITCODE -ne 0) { throw 'Model download or checksum verification failed.' }
    & $PythonCommand -m PyInstaller --noconfirm --distpath dist --workpath build FormulaSnip/FormulaSnip.spec
    if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
    Write-Output 'Built dist/FormulaSnip.exe. Run --self-test with a fresh output directory before releasing.'
}
finally {
    Pop-Location
}
