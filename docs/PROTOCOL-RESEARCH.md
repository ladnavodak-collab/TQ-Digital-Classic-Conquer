# Protocol research gate

The packet framing library is an isolated experiment, **not** a statement that Conquer Online patch 5065 uses this exact wire format. It currently assumes a 2-byte little-endian length inclusive of header, and rejects frames outside [2, 8192]. It is not connected to the TCP listener.

Before game protocol implementation: (1) obtain legally usable upstream server source and verify its license; (2) verify compatible client patch and authoritative packet layout; (3) document handshake, authentication, encryption, framing, and disconnect behavior; (4) add captured non-secret fixture tests with expected behavior; (5) integrate only after validation. Do not use real account credentials for diagnostics.
