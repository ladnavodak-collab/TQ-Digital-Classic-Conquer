# Standalone Diffie–Hellman packet: game TCP connection lifecycle

The original COPS v7 emulator's receive handler processed an incoming game-port Diffie–Hellman response and then fell through to encrypted game-frame parsing even when there were **zero trailing bytes**. The previous partial-frame hardening consequently closed a completely valid standalone DH connection.

The patch in `tools/patch_cops_dh_zero_tail.py` releases the receive allocation and returns without disconnecting **only when the DH packet has been fully consumed**. Short *nonempty* post-handshake fragments remain rejected pending proper encrypted TCP reassembly.

The disposable CI game integration check now transmits the DH response, waits 200 ms, then transmits the encrypted `MsgConnect` with an authenticated, single-use account transfer ticket in a **separate TCP send**. This tests the actual patched COPS C++ executable and distinguishes real packet-boundary tolerance from the old coalesced-only workaround.

Existing game login, character registration, persistence and relogin integration tests remain in the full workflow.

**Scope:** This is original diagnostic-client protocol coverage on loopback and synthetic map 1002, **not** proof of the proprietary 5065 client running or rendering a real Twin City map. General TCP frame fragmentation/reassembly is still outstanding.
