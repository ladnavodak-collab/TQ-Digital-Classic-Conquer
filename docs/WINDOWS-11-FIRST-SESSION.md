# Windows 11 first session — safe runbook

## Goal
Collect a reproducible toolchain report, build the tested foundation, and obtain an exact commit of the COPS v7 source for audit. **Not** a promise of login, gameplay, or public hosting during this session.

## Prerequisites
- Visual Studio 2022 Community with **Desktop development with C++** and Windows 11 SDK
- Git for Windows
- CMake 3.20+ (Visual Studio can supply CMake; add to PATH if using PowerShell)
- Qt and MySQL versions **not selected yet**. Inspect COPS project files and dependency requirements first; avoid downloading unsupported packages without a plan.
- Authorized, compatible client assets are a separate dependency; not included here.

## Steps
1. Extract the ZIP to `C:\Dev\TQ-Classic` (avoid putting builds inside Google Drive sync folders).
2. Open **Developer PowerShell for VS 2022**.
3. `Set-Location C:\Dev\TQ-Classic`
4. `powershell -NoProfile -ExecutionPolicy Bypass -File .\windows\Check-Environment.ps1 -OutputFile .\environment-report.txt`
5. `powershell -NoProfile -ExecutionPolicy Bypass -File .\windows\Build-Foundation.ps1`
6. `powershell -NoProfile -ExecutionPolicy Bypass -File .\windows\Get-COPS-Source.ps1`
7. Record commit ID from step 6. Inspect upstream license, Qt project configuration, third-party dependencies, packet format, database schema and client expectations before building upstream COPS.

The scripts are plain text and can be inspected before execution. Step 6 requires network access, writes only a new `upstream-cops-v7` folder, and refuses to overwrite an existing folder. No script exposes a network port, changes firewall rules, or installs software.

### If something fails
Copy **only** the console output and `environment-report.txt` into the chat after checking for sensitive paths/usernames. Never send passwords, authentication tokens, private keys, personal game accounts, or database credentials. Include the step number and exact error message.

### Security and deployment
Start with localhost, a dedicated test database, and non-production credentials. Do not port-forward, disable Windows Defender, or allow unsolicited inbound connections until authentication and input validation are independently tested. For public hosting, arrange backups, monitoring, shutdown procedures, and patching.

## Definition of progress
- Environment report obtained
- Foundation CMake build succeeds
- CTest output checked
- COPS git commit identified and source audited

These are **development setup milestones** only, not a playable server.
