COPS game-port initial Diffie–Hellman challenge smoke

The localhost-only probe in tools/cops_game_dh_proof_probe.py reads the actual COPS game-listener startup message. It decrypts the legacy Blowfish CFB64 stream using the known pre-exchange seed, validates size bounds and the TQServer seal, and parses the two IVs and public P/G/A DH parameters with strict length and hex checks. This checks a meaningful real game protocol milestone, beyond counting 333 challenge bytes.

OpenSSL deprecated Blowfish APIs are used only as a CI interoperability oracle; they are **not appropriate for a new secure public protocol**. The test is passive: it does not respond to DH, transfer tokens, authenticate a game session, or load characters. Run only against local COPS and synthetic map 1002. The separate account-port Argon2id authentication and transfer-token issuance tests remain in place.
