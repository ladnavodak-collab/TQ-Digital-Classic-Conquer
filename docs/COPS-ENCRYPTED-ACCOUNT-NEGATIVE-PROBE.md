Original COPS encrypted account-packet negative-path smoke

This small, localhost-only Python probe independently implements the client-to-server direction of the COPS TqCipher handshake using the two static 32-bit IV seeds and an incrementing byte counter. It creates a correctly framed 52-byte MSG_ACCOUNT (1051) encrypted frame with an intentionally unterminated 16-byte account name. Our previously merged account-field guard should reject that input without issuing an authentication response. It then reconnects to ensure the server survived. No real account credentials or protected client/game assets are required.

This is intentionally a **negative-path test** and must never be presented as a successful 5065 login, transfer ticket redemption, new-character registration or movement. It tests a single fully-buffered account-port frame, not TCP fragmentation or the DH/Blowfish game-port exchange.
