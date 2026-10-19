# COPS encrypted invalid game-port DH length smoke

On a disposable localhost-only COPS server with the synthetic test map, this probe reads the actual initial Blowfish-encrypted DH challenge then replies with an encrypted 11-byte prefix containing an invalid signed response length. The initial legacy Blowfish CFB key is taken from upstream COPS and encryption is performed with OpenSSL's legacy provider. Four hostile values are checked: negative, zero, oversized, and max signed integer. After each connection, a fresh game connection is tested and the server must continue emitting challenges.

This verifies the **negative key-exchange receive path** and server survival. It does not send a valid DH public key, decrypt gameplay, redeem a token, or enter Twin City. Keep this CI fixture isolated and never infer client compatibility from this result.
