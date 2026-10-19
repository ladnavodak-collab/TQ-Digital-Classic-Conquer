# First COPS pre-authentication loopback session smoke test

This test runs against the **actual hardened C++ COPS server executable** with the original synthetic 16x16 test-only map and disposable database. The Python client in `tools/cops_loopback_session_probe.py`:

1. Waits for localhost:9958 (account) and localhost:5816 (game).
2. Repeatedly opens/closes both TCP ports.
3. Reads the first bytes of the real server-generated Blowfish/Diffie-Hellman exchange request on game connections **without responding with any cryptographic payload**.
4. Reconnects once more after the disconnect callbacks to detect simple server crashes.

No real 5065 client, actual authentication, player creation, NPCs, movement, persistence or map rendering is involved. This only advances our milestone from port readiness to **pre-login protocol emission and connection lifecycle**. The probe never opens public network sockets.

The real next protocol milestone is authentic client-key-exchange compatibility, secure encrypted TCP reassembly, and a synthetic account-authentication test. No credentials are transmitted by this probe.
