Real COPS authenticated movement + persistence smoke

The disposable localhost client authenticates again, redeems a game ticket, loads the existing level-1 Trojan, enters the original flat 16x16 synthetic map 1002 and sends an encrypted MsgWalk east (direction 6). It verifies the actual COPS MsgWalk echo before disconnecting. On disconnect the real COPS Client::save path is expected to store the player's new position 9,8 rather than the original 8,8. A separate MariaDB query waits for the saved position and confirms CP and rebirth remain zero. A subsequent authenticated map entry probe verifies the position is loaded from SQL on another login.

This is a diagnostic synthetic map only. Not the retail 5065 client, rendered Twin City, or evidence of compatibility with commercial game assets. Do not expose development listeners publicly.

## First failure and correction

The first authenticated MsgWalk test crashed the original COPS process because our CI user table generated character ID 1. Upstream Entity::isPlayer accepts only IDs from 1,000,000 through 1,999,999,999. GameMap::enterRoom depends on that check before unpacking terrain cells. When the UID was outside that range the map-entry packets still appeared to succeed, but the cells were left packed; accessing them during movement could segfault. The disposable user table now starts auto-increment IDs at 1,000,000 and the actual COPS character loader rejects IDs outside the expected player UID range. This is an interoperability and safety requirement, not merely a test workaround.
