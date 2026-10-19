COPS character loading hardening

Upstream COPS used SELECT * for character reads while interpreting columns by fixed Player::SQLDATA_* ordinal positions. This patch uses the explicit 28-column projection from that enum, denies rows with zero player UID, nonzero CP, more than one rebirth or zero map ID before allocating a Player, and forces the actual COPS save path to persist zero CP.

These are actual server-side source changes compiled with the rest of the emulator, not only a test database. They do not prove a 5065 client login or validate all professions and map tiles. Alpha remains loopback-only.
