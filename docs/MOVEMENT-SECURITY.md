# v1.0 Movement security component

This is **not** a complete classic movement protocol and is not integrated into COPS. The numerical limits are **illustrative, not historical 5065 values**. The COPS v7 emulator README lists walking/jumping/portals among partly implemented systems (https://gitlab.com/conquer-online/servers/cops-v7-emulator).

## Implemented
- Server-side displacement rate validation using trusted monotonic timestamps.
- Distinct errors for uninitialized session, invalid coordinates, wrong map, rollback, too-fast displacement, and invalid policy.
- Rejects map changes except via a separate *trusted-handler-only* teleport API. The caller MUST authorize portal/teleport; the API itself does NOT authenticate requests.
- Rejected actions don't move the player. Rate windows are capped to avoid unlimited AFK accumulation.
- Works independently from graphics FPS; no reliance on client frame count.

## Must be addressed before live use
- Actual 5065 movement/jump formulas, movement packet schema, status effects and mount/skill exceptions.
- Walking terrain collision, map edges, legal jump path/landing, portal table validation.
- Explicit server-side sequence checks, session authentication, time/position validation under packet jitter and lag spikes.
- COPS code connection; concurrent update synchronization and movement history/auditing.
- Correctly tune per-map/per-movement speed from observed original 5065 gameplay.

## Security notes
- `authorized_teleport` must never be exposed directly to a client handler.
- Multiple moves in a single tick are limited by the configured burst allowance. This is a preliminary coarse validator, not an action-by-action rate limit.
- No claim of exploit-proof gameplay or a running game server.
