# Windows 11 client, launcher and anti-cheat specification — v0.8.1

Status: design requirements, NOT implemented. Target: classic patch 5065 client, subject to having a legally usable client and verifying binary/assets.

## Display / rendering
- Provide 1920x1080 windowed and borderless fullscreen options; 1024x768 fallback.
- Reflow HUD, chat, minimap, mouse targeting and clickable regions; keep world-camera geometry correct. Verify map edges, mouse-to-world transforms, portals, aspect ratio and UI alignment.
- FPS modes: 60, 120, 144, 240, and Uncapped (user requested unlimited). Display measured FPS, not inferred FPS.
- Decouple *rendering* from movement, attack timing, skill cooldowns and network simulation. Server decides gameplay timing. FPS changes must not change running speed, attack rate or stamina drain.
- Uncapped FPS can maximize CPU/GPU load. Recommend a user-selectable cap as default; test high refresh and minimized/background throttling.
- Compatibility unknown until exact client executable is acquired and tested. A 5065 client may require a native client patch or a replacement renderer. Neither has been implemented.

## Custom launcher
- Windows 11 x64 launcher; install to a user-writable app directory, no mandatory administrator rights.
- Launch game, choose resolution/display mode and FPS cap; server status, patch notes, and repair.
- Signed release manifest over TLS, per-file SHA-256, atomic staged updates and rollback. Verify digital signatures BEFORE trusting manifest/file list. Never execute arbitrary update scripts or download URLs from game packets.
- Restrict update paths to install directory, reject absolute/traversal/symlink paths, enforce payload size limits, check free disk space.
- Separate game configuration (user-controlled) from server security policy (server-controlled).
- Do not bundle original proprietary client assets without rights to distribute them.

## Anti-cheat (layered defense)
**Server authoritative**: inventory/silver updates, quest awards, XP, damage, position, spell costs, cooldowns, equip requirements, rebirth, class restrictions and teleport validation.
- Per-session sequence/timestamp consistency checks; reject impossible movement over elapsed time with allowances for latency/jumps/server teleports.
- Enforce action rate limits using monotonic server time; replay prevention and packet length/type validation.
- Financial transactions require atomic database commits and idempotency keys; double spend and item duplication regression suite.
- Validate all client supplied IDs and counts against server state, not text or local config.
- Tamper evidence: launcher verifies signed game files; this does **not** replace server validation and can be bypassed on the client.
- Security logging, audit events, appealable enforcement, tuneable thresholds; avoid permanent bans solely on heuristics.
- First release should avoid invasive kernel drivers, broad process surveillance, disabling security tools, or collecting unrelated personal files.
- Maintain a threat model and run fuzzing/property tests on packet parser and economy code.
- Operate LAN-only until authentication, rate limiting, logging, backups and rollback are validated.

## Prerequisites / acceptance tests
- Exact unmodified client build and checksum identified, redistribution permission clarified.
- 1920x1080 renders without black margins, click-offset bugs, clipped UI, or exploitable target range.
- Run same movement, jump, PvP, and attack test at 30/60/144/240/uncapped; resulting authoritative gameplay state must be equivalent within expected network jitter.
- Damage, heal, XP, silver, quest rewards remain server-authoritative under forged/replayed packets.
- Launcher rejects tampered manifest, corrupted payload, path traversal, downgrade and partial update; supports interrupted-download recovery.
- Target platform Windows 11. No production anti-cheat or launcher has yet been released.

## Research references and caution
- Community wiki https://wiki.conqueronline.net/ is useful for understanding classic mechanics, but is not an original 2008 patch-5065 specification. Flag custom server changes explicitly.
- https://www.elitepvpers.com/forum/co2-programming/5287363-need-help-client-resolution-5065-a.html reports practical widescreen changes to client 5065; anecdotal, not a verified implementation for our binary.
- https://playconqueronline.com/guides/launcher-widescreen documents another server's update/repair and F11 widescreen UX; design inspiration only.
- https://github.com/deklol/Preservation-CO-Client is a Rust rendering skeleton, not a complete C++ client/server.
