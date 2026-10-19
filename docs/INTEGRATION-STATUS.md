# Integration status — v0.4.0

- Candidate upstream: https://gitlab.com/conquer-online/servers/cops-v7-emulator (patch 5065).
- 2026-10-19: `git ls-remote` failed because the environment could not resolve gitlab.com. Upstream code, licensing and actual build were NOT audited.
- Rules are independent of the emulator and are NOT wired into a networked game server.
- SQLite-backed daily claims persist and use a composite primary key. Reward grants MUST be committed in the same transaction as claims before this can be used for a real economy.
- The database module is optional at build time. Install SQLite3 development headers to enable it.
- Google Drive link provided by the user is not directly accessible through an available connector; this release is supplied as a downloadable ZIP.
