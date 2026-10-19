# Synthetic COPS map-1002 boot probe

This generator creates a **new, original**, flat 16x16 diagnostic DMap with valid COPS-style row checksums, zero passages and zero visual layers, plus GameMap.ini mapping `Map1002` to the generated filename. The map is deliberately only a **test fixture**, not Twin City scenery, official game geometry, or a playable client asset.

COPS upstream `MapData::loadMapData` reads a 276-byte header, 6-byte cell records and 4-byte row checksums, followed by passage/layer counts; our fixture follows those contracts and is unit-tested.

The intended CI probe provides the *six empty loader tables* and one synthetic `map` row with `id=1002`, `doc_id=1002`. If the actual hardened server starts listening, that demonstrates a limited **server boot smoke test only**; it does not demonstrate login, account schema, skills, scenes, player movement, network-fragment handling, rendering or save/relogin. The server must remain bound to loopback. If the upstream client expects a different DMap or a map size, the synthetic map must NEVER be passed off as real 5065 game content.
