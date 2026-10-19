# First COPS world-entry protocol smoke (test-only)

This extends the verified authenticated character-create/save/relogin CI path to request `MsgAction::ACTION_ENTER_MAP` with an existing saved classic Trojan. A localhost-only original Python protocol client negotiates encrypted COPS game DH, redeems a fresh single-use ticket, validates the saved `MsgUserInfo`, then sends the correctly framed encrypted map-entry action.

The test checks that the actual C++ COPS server replies with a matching `ACTION_ENTER_MAP` (map document 1002, position 8/8), an `ACTION_MAP_ARGB` lighting update and a `MsgMapInfo` containing map UID and document UID 1002. These messages are decoded from the continuous encrypted Blowfish/CFB64 session, with packet framing tolerant of short TCP reads.

**This is not a playable game or retail client test.** Map 1002 is an original 16×16 synthetic test fixture, not official or customized Twin City art. No 5065 client rendering, visible character, movement, world persistence, NPCs or full map compatibility is established. Legacy fragmented DH+MsgConnect support is still pending. Keep development ports loopback-only.
