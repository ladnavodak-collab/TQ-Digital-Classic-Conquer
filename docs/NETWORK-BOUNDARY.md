# Network boundary — v0.5.0

The `tq_tcp_diagnostic` executable is a **loopback-only diagnostic TCP listener**, not a game server. It listens on 127.0.0.1 on the explicitly supplied port, accepts connections, sends a plain-text diagnostic response, and closes them. It does not implement login, encryption, packet framing, game-state mutation, persistence, or the Conquer Online protocol.

Example: `./build/tq_tcp_diagnostic 9958` (development only; do not configure a Conquer client to connect to it).

Security boundaries: no external bind, no account credentials, no client asset distribution. The current loop has no graceful shutdown handling, connection rate limits, or protocol parser. These are required before any real network-facing service.

Integration gate: acquire upstream source; review licensing and patch 5065 protocol compatibility; reproduce build; establish a documented packet-framing layer and negative tests; only then add authentication and world entry. No upstream code has been integrated.
