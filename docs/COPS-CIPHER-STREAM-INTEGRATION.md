# Stateful COPS stream-decryption integration boundary

The `tq_cipher_stream_bridge` component demonstrates one connection-owned cipher with bounded **post-handshake** decryption and plaintext frame buffering. Unit tests use a toy, stateful XOR cipher to prove that fragmentation does not cause re-decryption, and coalesced encrypted frames are parsed successfully.

**The toy cipher provides NO security and is test-only.** This component is NOT wired to COPS. COPS has separate account and game sockets, a Diffie-Hellman key exchange, Blowfish and TQ cipher variants, and a client seal marker. The current bridge does not decode these legacy handshake packets and cannot perform game login.

Why integration is not yet safe:
- The `Client::KEY_EXCHANGE` state must consume only the exact bytes belonging to the handshake before switching cipher epochs, including fragmentation/coalescing.
- Post-handshake decryptions must preserve cipher state and parse the TQClient seal where applicable.
- A real client and legal 5065 fixture packets must be used to verify protocol framing and field lengths.
- The current plaintext frame cap comes from legacy code, not a verified 5065 specification.
- Cipher dispatch and frame processing need robust disconnect/reentrancy and lifecycle tests.
- Credential and database flaws remain outstanding.

**Release gate:** Do not deploy the COPS emulator to a public network or call it playable based on this isolated transport test. The next patch must implement an upstream-compatible handshake state machine and an integration test with the actual COPS cipher.
