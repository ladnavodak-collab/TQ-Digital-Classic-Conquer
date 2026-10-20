# Playable server release gate (patch 5065)

This file defines what **"ready to launch a playable local server"** means. A green compile and diagnostic TCP listener do **not** satisfy it.

## Verified today
- [x] COPS v7 source can be fetched and compiled on an ephemeral Ubuntu Qt5 CI runner (build only).
- [x] Independent C++ foundation modules have automated tests on Windows and Ubuntu.
- [x] Rust foundation compiles in CI; Windows graphical shell is compile-checked (not run).

## Blocked / not proven
- [ ] Obtain and verify permitted patch-5065 client files and required DMaps / resource files.
- [ ] Identify precise COPS upstream commit and preserve its license notices; resolve original LICENSE conditions before redistribution.
- [ ] Provide disposable MySQL instance with a compatible, reviewed schema and non-root restricted SQL credentials.
- [ ] Patch COPS to fail closed on missing configuration and insecure legacy authentication (tracked in issue #5).
- [ ] Patch and fuzz COPS packet receive / key exchange boundaries, including partial reads, oversized payloads and unexpected disconnects (issue #7).
- [ ] Start account and game services bound to loopback in a disposable test environment, with health checks and shutdown behavior.
- [ ] Prove a real compatible client authenticates using test credentials.
- [ ] Prove character creation / selection and persistence across server restart.
- [ ] Prove map loading, enter Twin City, walking/jumping, portals, and reliable disconnect/reconnect.
- [ ] Test economy rollback, item ownership, NPC transaction replay, daily quest claims, server-authoritative movement.
- [ ] Enforce classic-only class allowlist, first rebirth only, no CP or mall in server-side actions.
- [ ] Document reproducible local launch steps and backup/restore verification.
- [ ] Security review / crash testing, no external port forwarding during local validation.

## Testing stages
1. **Buildable**: compiler and unit tests pass, no game login implied.
2. **Bootable**: services and database start cleanly on loopback, configuration secrets excluded from logs.
3. **Connectable**: real client completes authenticated session.
4. **Playable local alpha**: account creates character, enters a map, moves, saves, relogs.
5. **Online release candidate**: feature coverage, backups, threat model and sustained soak tests pass.

The current known status is **buildable foundation**, not yet **bootable/connectable**.

## Integration ownership
- Server: fork COPS upstream after pinning version; fix authentication, DB, packets and gameplay.
- Client: Rust shell is not yet protocol-compatible or game-feature complete.
- Infrastructure: CI runners are temporary and do not host an always-on server.
- Testing: use only authorized game data and legally available client files.

## Relevant trackers
- [Authentication and DB security](https://github.com/ladnavodak-collab/TQ-Digital-Classic-Conquer/issues/5)
- [Packet parsing and exchange safety](https://github.com/ladnavodak-collab/TQ-Digital-Classic-Conquer/issues/7)
