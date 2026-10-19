# Explicit upstream clone into a separate directory. Does not execute upstream code.
param([string]$Destination = '')
$ErrorActionPreference = 'Stop'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git not found. Install Git for Windows first.' }
if ($Destination -eq '') { $Destination = Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..')).Path 'upstream-cops-v7' }
if (Test-Path -LiteralPath $Destination) { throw "Destination already exists; refusing to overwrite: $Destination" }
$repository = 'https://gitlab.com/conquer-online/servers/cops-v7-emulator.git'
Write-Output "Cloning $repository to $Destination"
git clone -- $repository $Destination
if ($LASTEXITCODE -ne 0) { throw 'Clone failed; check network and repository access. No source was altered.' }
git -C $Destination rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Unable to identify fetched commit.' }
Write-Output 'STOP: Audit upstream license/dependencies before trying to compile or run it.'
