# Authenticated character relog and MsgUserInfo smoke

After the live registration probe has created a level-one Trojan account character on synthetic map 1002, this test reconnects to the real COPS game listener on localhost, completes DH key exchange, requests a newly authenticated account-to-game ticket, and decrypts the server's gameplay packets.

It parses complete packets with their per-message `TQServer` seal across arbitrary TCP read boundaries and asserts that the game server emits `MsgUserInfo` for the **existing** saved character. The packed packet is verified against the classic stats, profession, level, HP/MP, zero CP and zero rebirth. This follows the real COPS `Database::getPlayerInfo` and `World::addPlayer` path.

**Limitations:** This is a synthetic protocol client. It does not prove the retail 5065 executable can log in, render Twin City, move, or persist live-world updates. The map is an original 16x16 CI fixture. COPS still requires DH reply and the first game packet in the same TCP read, a known protocol correctness limitation. Do not open public network listeners.
