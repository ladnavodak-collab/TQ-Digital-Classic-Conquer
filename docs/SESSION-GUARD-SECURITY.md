# Session guard: security primitive, not full anti-cheat

`src/session_guard.*` is a protocol-agnostic, per-session server-side guard for strictly increasing sequence identifiers and per-action cooldowns measured with a **server-owned monotonic clock**. All cooldown durations and action types must be chosen on the server. Never trust timestamps, delay values, class permissions or identifiers provided by a game client.

## Guaranteed by the isolated unit tests
- Reject zero sequence and zero action ID.
- Reject stale and repeated sequences.
- Reject actions before the cooldown expires; independent per action type.
- Reject backward clock values.
- Avoid cooldown arithmetic wrap-around near the maximum integer value.
- Reset internal state explicitly when establishing a new authenticated session.

## Not guaranteed / release blockers
- Not connected to TCP, auth or COPS v7. No Conquer packet IDs or crypto verified.
- Sequence numbers on actual Conquer wire packets may not exist; mapping must be designed only after protocol audit. In that case, enforce authenticated session-specific request identity or safe server-side operation IDs instead.
- This check does not validate speed hacks, positions, packet signatures, login, item transactions or economics.
- The state is single-threaded per connection; callers must synchronize across threads.
- Cooldown failure consumes the sequence; higher layer must use new sequences on subsequent actions.
- At UINT64_MAX, a mathematical cooldown cannot be represented past the boundary; production monotonic counters are never expected near wrap, but the limit requires explicit operational testing.
- Client-integrity checks alone do not prevent cheating; server authority is the primary defense.

## Next integration gates
1. Audit COPS v7 code to determine where authenticated sessions and game actions are dispatched.
2. Define a rule table with action IDs, cooldowns, map effects, skill and class permissions.
3. Place validation *after authentication but before state mutations*.
4. Add integration tests that send forged and replayed network messages and verify no game state change.
5. Add controlled performance tests, audit logs and configurable detection policy.
