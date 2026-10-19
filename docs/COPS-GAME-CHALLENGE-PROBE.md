COPS game-port DH challenge decoding

A localhost-only diagnostic connects to the **real patched C++ COPS game port 5816**, captures the first server-generated challenge, decrypts it using a tiny helper built from upstream COPS' own Blowfish CFB64 source and its fixed pre-exchange seed, then parses the declared sizes, junk, two IVs, DH P/G/A hexadecimal fields and the server seal. Values are never disclosed in CI logs; only lengths are printed.

This validates challenge encoding and makes progress toward a compatible game login. It does NOT send a client DH response, derive shared keys, redeem the authenticated transfer ticket or enter the game world. This test uses the original synthetic map 1002, not proprietary client assets. Server remains loopback-only.
