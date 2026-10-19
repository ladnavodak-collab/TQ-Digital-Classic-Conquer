# Build and test only our isolated foundation, not upstream COPS.
param([string]$Configuration = 'Debug')
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$build = Join-Path $root 'build-win'
if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) { throw 'CMake not in PATH. Install CMake and reopen terminal.' }
cmake -S $root -B $build -A x64 -DBUILD_TESTING=ON
if ($LASTEXITCODE -ne 0) { throw 'CMake configure failed.' }
cmake --build $build --config $Configuration
if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
ctest --test-dir $build -C $Configuration --output-on-failure
if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
Write-Output 'Foundation build/tests complete. This is not a playable game server.'
