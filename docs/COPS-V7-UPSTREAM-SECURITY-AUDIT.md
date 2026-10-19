# COPS v7 upstream audit — 2026-10-19

## Provenance and release gate
- Target: patch **5065** COPS v7 emulator; **not** yet compiled or integrated.
- Primary upstream: https://gitlab.com/conquer-online/servers/cops-v7-emulator (master commit shown by GitLab: `84919e25`; obtain full commit SHA before pinning).
- Archived public mirror, read-only: https://github.com/cptsky42/COPS-v7-Emulator
- Upstream project file: `COPS v7 Emulator.pro`, Qt4/Qt5 `core network sql`, Qt Concurrent on Qt5, in-tree Lua 5.2.3, LZ4 r123 and bigint sources.
- Upstream README explicitly says major game functionality remains incomplete. It has historically been tested on older operating systems; current Windows 11/Qt build is **not verified**.
- GitLab labels upstream BSD 2-Clause, **but the actual mirrored LICENSE text includes four numbered conditions**, including an advertising acknowledgement. Treat the precise license obligations as **unresolved pending legal review**, especially before redistributing modified binaries/source. Retain original notices.
- Do **not** add proprietary client binaries, client assets, game data, production credentials or private keys to this repository.
- No COPS source is vendored yet; this audit records exact upstream files inspected using authenticated GitHub read access.

## Source-level findings
| ID | Severity | File | Evidence | Required remediation |
|---|---|---|---|---|
| COPS001 | High | `data/settings.cfg` | Sample `SQL_USER = root` | Dedicated DB account with least privilege. |
| COPS002 | Critical | `data/settings.cfg` | Sample `SQL_PWD = root` | Remove default credential, require runtime secret injection, deny startup on sample config. |
| COPS003 | Critical | `src/Database/database.cpp` | `password.compare(aPassword) == 0` | Replace plaintext comparison with vetted Argon2id/bcrypt login flow, hash migration strategy and lockout controls. |
| COPS004 | High | `src/Database/database.cpp` | Logs SQL after interpolating bound values with `getSqlCommand` | Avoid logging SQL parameter values, especially account credentials. |
| COPS005 | Research | `src/Network/msgwalk.cpp` | Checks player's UID and derives move from packet direction, moves player | Ensure server-side speed, collision, map and action-rate validation after verifying actual packet flow; current code only partially verified. |
| COPS006 | Build | `COPS v7 Emulator.pro` | qmake project, Qt MySQL driver required | Build pinned upstream on Windows/Linux CI; add build reproducibility, dependency inventory and startup smoke tests. |

Do not construe these as an exhaustive security review.

## Minimum integration gates
1. Pin full upstream commit hash; verify source archive integrity and detailed license terms.
2. Build unchanged upstream inside an isolated environment without adding any proprietary assets.
3. Deny use of sample credentials and plaintext authentication in the integrated server.
4. Use app-scoped DB credentials; bind service to loopback for local testing.
5. Add source-level regression checks for sensitive logging and legacy authentication.
6. Validate actual 5065 protocol, movement, world entry and item transactions against controlled test client.
7. Only after passing security, load and persistence tests consider external hosting.

## Offline audit tool
`python -m tools.audit_cops path/to/cops-v7 --output cops-audit.json`

Returns exit code 1 for high/critical findings. Report describes patterns without echoing found secret values. It is deliberately scoped to four known red flags; a clean result does *not* prove the software safe.
