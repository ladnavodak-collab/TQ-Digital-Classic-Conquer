# Account-to-game transfer tickets (single-process alpha)

COPS originally generated a login-transfer integer on the account listener without checking it when a client sent MsgConnect on the game listener. That allowed any client which completed the game-port Diffie-Hellman exchange to supply an arbitrary account UID. The new `tools/patch_cops_transfer_tickets.py` introduces an in-memory ticket registry shared by both listener handlers in the same COPS process.

- Only a successfully authenticated account is issued a transfer token; the token uses Qt's system random generator, not `rand()`.
- A game-port MsgConnect must match both the claimed account UID and the token, and consumes the token before loading a character from SQL.
- Tokens expire after **30 seconds**, are single-use, and storage is bounded to 4096 pending entries. New successful logins invalidate prior unused tickets for the same account.
- The game listener remains loopback-only, and failed/unissued/expired/replayed tokens are rejected.
- This is an **alpha single-process** design. No external game server, clustered nodes, restart persistence, remote IP trust, or multi-device semantics are supported. 31-bit tokens are a legacy protocol constraint; do not expose the server publicly based on this safeguard.
- This does NOT by itself prove correct encrypted 5065 client authentication; full encrypted TCP stream reassembly and login integration tests remain outstanding.

The new server-side token checks are included in the real COPS Qt5/MariaDB smoke compile and separately tested with a C++ QtCore test where possible.
