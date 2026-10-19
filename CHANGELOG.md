## v1.1.0 — Original Rust client-settings foundation
- Added independent Rust CLI for generating and validating 1920x1080/display/FPS settings.
- Added Rust unit tests (not executed: Rust toolchain absent in build environment).
- No GUI, packet protocol, renderer, launcher or auto-clicker implemented.

# Changelog

## v0.6.0 — Packet framing experiment
- Added a standalone length-prefixed C++ packet-framing experiment with input bounds and unit tests.
- Added protocol research gate. No claim of Conquer client compatibility.

# Changelog

## v0.5.0 — Diagnostic network boundary
- Added cross-platform loopback-only TCP diagnostic listener (`tq_tcp_diagnostic`).
- Added port validation and CTest invalid-port check.
- Documented clear boundary between diagnostic networking and a compatible game server.
- Upstream COPS v7 clone still blocked by DNS/network restrictions; no game protocol integration.

## v0.4.0
- Persistent SQLite daily quest claim store and tests.
- Classic rules foundation retained.

## v0.7.0
- Added Windows 11 development environment report, separate foundation build/test helper, upstream COPS source clone helper, and safe first-session runbook.
- Upstream source build and real client connectivity remain unverified.

## v0.8.1 — Client / anti-cheat planning
- Documented 1920x1080, FPS modes including uncapped, signed launcher patching, and server-authoritative anti-cheat requirements.
- Added explicit compatibility and security acceptance criteria; no client or anti-cheat implementation is claimed.
- Flagged supplied community wiki as secondary version-sensitive evidence.

## v0.9.0 — Anti-replay/rate guard prototype
- Added isolated C++ per-session monotonic sequence and action cooldown guard.
- Added unit tests for replay, cooldown, clock rollback, input rejection and integer saturation.
- No real client traffic or upstream COPS code integrated yet.

## v1.0.0 — Movement guard
- Added protocol-independent server-controlled movement speed/map/bounds validation and tests.
- Added trusted-only teleport reset and explicit deployment limitations.
- No COPS integration, real login, or playable game claimed.

## v1.2.0 — Original graphical Rust client shell
- Added optional `minifb` window demo with custom software framebuffer UI, FPS display, pointer crosshair and Escape key.
- Applied existing resolution, borderless/windowed and capped/uncapped settings.
- Added Windows validation guide; Rust compile is unverified in this environment.
- No game protocol, renderer, server, automated clicks, or third-party client source included.

## v1.3.0 — Transactional economy prototype
- Added C++ SQLite test ledger for atomic silver transfers and item purchases.
- Added idempotency keys and request fingerprint conflict rejection.
- Added tests for duplicated requests, ownership checks, insufficient funds, amount validation and overflow.
- No COPS integration or production economy claims.
