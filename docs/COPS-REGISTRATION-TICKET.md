COPS registration authorization gate

The original MsgRegister handler re-authenticated plaintext credentials on the game connection and did not demand proof that its account-to-game transfer token had ever been redeemed. This patch adds a per-Client flag initialized false, set only after successful MsgConnect transfer-token redemption, and required before character registration. It also checks account UID consistency, ensures the player isn't already present and rejects unterminated fixed-size register packet strings before using them as C strings.

This is real upstream C++ source patched during the full CI Qt5 build. It does not prove a 5065 client can complete its encrypted handshake; it also does not solve TCP stream reassembly. Keep the development server bound to loopback. The register packet still carries a legacy password field, which this path no longer uses for database authentication.
