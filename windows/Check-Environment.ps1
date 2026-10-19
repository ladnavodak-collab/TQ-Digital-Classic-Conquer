# Read-only toolchain check. No software installations or system modifications.
param([string]$OutputFile = "")
$ErrorActionPreference = 'Continue'
$names = @('git', 'cmake', 'ninja', 'cl', 'qmake', 'qtpaths', 'mysql', 'winget')
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('TQ Classic Windows 11 environment check')
$lines.Add("Timestamp: $(Get-Date -Format o)")
$lines.Add("PowerShell: $($PSVersionTable.PSVersion)")
$lines.Add("OS: $([System.Environment]::OSVersion.VersionString)")
$lines.Add('')
foreach ($name in $names) {
    $command = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $command) {
        $lines.Add("${name}: NOT IN PATH")
    } else {
        $lines.Add("${name}: $($command.Source)")
    }
}
$lines.Add('')
$lines.Add('Note: Visual Studio cl.exe is normally available in a Developer PowerShell, not a standard terminal.')
$lines.Add('Do not paste passwords, tokens, or private connection strings into bug reports.')
$lines | ForEach-Object { Write-Output $_ }
if ($OutputFile -ne '') {
    $lines | Set-Content -LiteralPath $OutputFile -Encoding UTF8
    Write-Output "Wrote report to $OutputFile"
}
