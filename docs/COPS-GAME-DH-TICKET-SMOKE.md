# Authenticated COPS game-port Diffie–Hellman and ticket redemption (CI)

This milestone uses the **real hardened COPS Qt5 executable** on loopback, the disposable Argon2id test account, and original 16×16 synthetic map 1002. It does not require a proprietary 5065 executable or unverified game assets.

The test-only C++ `cops_blowfish_bridge.cpp` links the upstream COPS Blowfish CFB64 implementation. This avoids an incompatible library key-length limit: COPS's derived DH shared key may exceed the conventional Blowfish 56-byte maximum. The Python smoke test:

1. Logs into the account port with a verified disposable account, extracting a short-lived, single-use transfer ticket.
2. Connects to localhost game port 5816, decrypts and checks the genuine server DH challenge and Blowfish IVs.
3. Responds with its generated DH public key, letting COPS establish the shared key.
4. Sends a separate encrypted MsgConnect with the issued ticket and expects a decrypted MsgTalk entry response indicating the new-character path.

The C++ zero-tail patch fixes a concrete TCP lifecycle bug: a complete DH response not accompanied by a game packet previously fell through to a too-short-frame disconnect. Incomplete nonempty encrypted tails remain rejected until robust TCP stream reassembly is integrated.

**Limitations:** This tests a freshly implemented diagnostic client, **not** the real 5065 Windows game executable. It exercises ticket redemption and the new-role response; it does not yet create a character, render Twin City, load inventory, move a player, prove retail compatibility, or justify opening network access. Actual world tiles are original synthetic fixtures only.
