# DeepSeek TUI Launcher
#Requires -Version 5.1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Try Windows Terminal first (best Unicode support)
$wt = Get-Command "wt.exe" -ErrorAction SilentlyContinue
if ($wt) {
    Start-Process wt.exe -ArgumentList "-d ""$ScriptDir"" pwsh -NoExit -Command python main.py"
    exit
}

# Fallback to PowerShell with UTF-8
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

python main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press any key to exit..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
