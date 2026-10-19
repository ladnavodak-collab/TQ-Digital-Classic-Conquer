# TQ Digital — Classic Conquer Foundation

Status: planning and build-scaffold stage. This is **not** a playable Conquer Online server.

## Goal
Create a maintainable C++ server foundation for a classic-era Conquer Online experience:
- no Ninja or later classes
- one rebirth maximum
- no CP economy or shopping mall
- editable NPCs, quests, items, and world content
- daily quests with server-side validation and persistent completion state

## Current recommendation
Evaluate client patches 4294 and 5065 before committing to a protocol. COPS v7 is a C++/Qt project targeting 5065, but its own documentation describes it as a base source with many incomplete features. Treat it as a research candidate, not a ready server. Comet documents multiple patches, including 4294 and 5065, but is C#.

References:
- https://gitlab.com/conquer-online/servers/cops-v7-emulator
- https://github.com/conquer-online/comet
- https://conquer-online.github.io/wiki/

## What is in this package
- `docs/SOURCE-SELECTION-REPORT.md`: evidence-based source candidate audit
- `docs/DECISION-LOG.md`: version/source decision notes
- `docs/ARCHITECTURE.md`: proposed architecture
- `docs/ROADMAP.md`: staged implementation and acceptance criteria
- `docs/RISK-REGISTER.md`: known risks
- `docs/GOOGLE-DRIVE.md`: proposed Drive workflow
- `src/main.cpp`: tiny C++ scaffold executable
- `CMakeLists.txt`: minimal CMake build
- `tests/README.md`: initial test strategy

## Build the scaffold
Requirements: CMake 3.20+ and a C++17 compiler.

```sh
cmake -S . -B build
cmake --build build
./build/tq_classic_scaffold
```

On Windows, run `build\\Debug\\tq_classic_scaffold.exe` or `build\\Release\\tq_classic_scaffold.exe`, depending on your generator.

Expected output:
`TQ Digital Classic Conquer scaffold: OK`

Verified in the current build environment with CMake 3.31.6 and C++ compiler 14.2.0. This only verifies the development toolchain and project skeleton. It does not implement networking, authentication, game mechanics, or client compatibility.

## Next required input
Before a real server implementation, choose the target client patch and audit a source base, client files, protocol compatibility, license, dependencies, and build reproducibility. Do not use copyrighted game assets unless you have the right to use them.

## v0.5.0: TCP diagnostic only
Run `./build/tq_tcp_diagnostic 9958` to start a **loopback-only** TCP smoke-test listener. This is not a compatible Conquer server; it sends a diagnostic text response and closes connections. See `docs/NETWORK-BOUNDARY.md`.

## v0.6.0
Added isolated generic packet-framing experiment with tests. **Not a verified Conquer packet format.** See `docs/PROTOCOL-RESEARCH.md`.

## v0.7.0 — Windows 11 setup kit
See `docs/WINDOWS-11-FIRST-SESSION.md` and the inspectable PowerShell scripts in `windows/`. These scripts have not been executed on a Windows 11 machine; they do not install dependencies or run a Conquer server.

## v0.9.0 — Security module
Added `tq_session_guard` with tests for server-owned cooldown validation and replay detection. This is standalone code, **not an integrated anti-cheat, login server or game server**. See `docs/SESSION-GUARD-SECURITY.md`.

## v1.0.0: Movement validation building block
`src/movement_guard.*` is a protocol-independent speed/coordinate/map guard, **not** verified 5065 mechanics or a client-connected server. See `docs/MOVEMENT-SECURITY.md`.

## Rust client track (v1.1.0)
`rust-client/` contains an original **settings-only** Rust CLI. See `docs/RUST-CLIENT-FOUNDATION.md`. This does not connect to the game server.

## v1.2.0 graphical Rust shell
A window-rendering smoke test has been added in `rust-client/src/bin/client_window.rs`; run with the optional Cargo feature `graphics`. This is an **original demo UI, not a playable client**, and has not yet been built or run on Windows 11. See `docs/GRAPHICAL-RUST-CLIENT-V1.2.md`.

## v1.3.0 economy prototype
`src/economy_ledger.*` adds SQLite-backed transactional silver transfers and item purchases, with a standalone CTest target. It is not a playable server or a game packet handler. See `docs/ECONOMY-LEDGER.md`.
