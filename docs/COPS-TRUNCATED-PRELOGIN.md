# Pre-login truncated receive hardening

The original COPS receive handler allocates a temporary byte buffer and processes a client-provided key exchange frame. After a successful exchange, a short remaining tail can enter the default case and return without freeing that buffer. The patch `tools/patch_cops_receive_cleanup.py` adds cleanup and fail-closed disconnect in this specific path.

The live CI probe sends deliberately truncated one-byte payloads to **localhost-only** account (9958) and game (5816) listeners, closes sessions, reconnects and verifies fresh game-prelogin exchange bytes and server survival. This does not simulate a valid client key exchange or prove client 5065 authentication. The current code rejects incomplete frames; proper encrypted TCP stream reassembly (and secure per-connection buffering) is still necessary to accept legitimate fragmented gameplay traffic.

This patch is applied to a disposable upstream COPS checkout after the existing bounds and DH validation patches. Never enable external network exposure based on these smoke checks.
