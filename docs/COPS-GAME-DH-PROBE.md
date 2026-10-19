COPS game-port DH challenge inspection

The game server generates an encrypted Blowfish CFB64 challenge on localhost TCP 5816 before account-ticket redemption. This Python CI probe decrypts the initial COPS challenge using the public, upstream initial handshake key and validates the packet length, 12-byte junk region, two 8-byte IVs, hex-encoded DH prime, generator 5 and server public key. Strict bounds checks reject malformed components. Parsing is read-only: the probe sends no DH response and cannot enter the world.

The old COPS protocol is not a modern secure transport and this diagnostic must never justify exposing the development listeners publicly. Successful handshake parsing does not prove a real Conquer 5065 client login, game-ticket consumption or character load.
