# COPS Diffie-Hellman payload validation (experimental upstream patch)

`tools/patch_cops_dh_validation.py` applies stricter input checks to the upstream COPS `MsgLoginChallengeS::process` implementation, which previously advanced an unchecked pointer by an attacker-controlled signed junk length, allocated memory using an unchecked public-key length, and converted a potentially long derived key into a fixed 256-byte array.

It validates advertised size, non-negative junk length, actual buffer boundaries, public-key hex encoding/length, and derived seed length before using them. This is an isolated patch applied to a temporary upstream checkout, not a complete protocol implementation.

**Known follow-up:** The upstream `MsgLoginChallengeS` constructor's big-endian swap routine also reads unchecked offsets before `process()`; that must be made safe before supporting big-endian clients/servers. The upstream socket's encrypted stream handling is still not fragmented-TCP safe. This patch depends on the separately tested receive bounds patch. We do **not** enable public hosting.

CI compiles a temporary upstream checkout with both patches applied; it does not perform a real client handshake or authenticate a user. No playable-client claim is made.

Before release: pin full upstream commit, confirm message format against legitimate patch 5065 fixtures, implement cipher-aware buffering and handshake transition, replace plaintext password verification, test database setup and world entry.
