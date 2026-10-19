# TCP stream reassembly research module

The standalone `tq_stream_reassembly` C++17 module parses **decrypted plaintext** packets of the form `uint16_t length + uint16_t message_type` in little-endian byte order. It handles split headers and split bodies, multiple packets per receive, and bounded queues. It rejects invalid length values, null pointer/nonzero length input and memory exhaustion attempts.

This module is **not integrated** into COPS's TCP listener. Upstream COPS performs stream cipher operations and Diffie-Hellman exchange; simply applying this plaintext parser to encrypted bytes would be incorrect. A production integration must own per-connection encrypted input buffers, preserve cipher state across fragmentation, decode the legacy handshake safely, handle TQ seal bytes, and not assume Qt readyRead boundaries match message boundaries.

Packet size cap 1024 matches an upstream COPS receive check, not a verified complete specification for every 5065 message type. Limits may need adjustment after test vectors confirm the legitimate maximum.

Before integration:
- Capture legal, non-sensitive 5065 handshake and packet *test vectors*.
- Audit `src/server.cpp`, `src/client.cpp`, `src/Network/Sockets/networkclient.cpp` together.
- Replace strict fragment disconnect with proper encrypted stream handling.
- Test split key exchange, fragmented encrypted messages, repeated packets and packet seal handling.
- Use sanitizers and fuzzing on the complete decoder.
- No external hosting until authentication and packet parsing are hardened.

Run `cmake -S . -B build -DBUILD_TESTING=ON && cmake --build build && ctest --test-dir build --output-on-failure` in the foundation repository.
