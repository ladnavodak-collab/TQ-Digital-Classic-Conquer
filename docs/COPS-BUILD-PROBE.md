# Upstream COPS v7 compile probe

The workflow [COPS v7 upstream build probe](../.github/workflows/cops-upstream-probe.yml) fetches an unmodified public COPS v7 GitHub mirror on a temporary Ubuntu runner, compiles it using Qt5 qmake, and stores diagnostic logs for seven days.

It **does not run the server**, connect to a game client, import databases, or copy upstream COPS files into this repository. It does **not** imply a playable server.

## Why this gate matters
- COPS v7 is incomplete; the build may fail on modern Qt5/C++ compilers.
- The project relies on Qt Network, SQL, Concurrent and the MySQL Qt driver, plus bundled old C/C++ dependencies.
- An exact upstream commit SHA is recorded in `upstream-commit.txt` for reproducibility and later pinning.
- The unmodified upstream still contains insecure sample database credentials and plaintext credential comparison; **do not deploy it**.
- The LICENSE includes obligations that require review before redistribution or incorporation.

## Acceptance
1. Upstream fetch succeeds; pinned SHA is captured.
2. Unmodified upstream can be compiled, or failures are triaged and documented.
3. Separate hardened fork/patch must pass authentication, database, packet, movement and economy tests.
4. Verified compatible client logs in, creates a character, enters a map, walks, saves and reloads.
5. Only after the above can the project be called **playable**.

This workflow is private-repository CI. GitHub-hosted build machines are temporary and are not a continuously running game host.
