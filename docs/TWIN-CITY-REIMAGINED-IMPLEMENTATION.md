# Twin City Reimagined — implementation contract v1

**Map ID 1002.** The user-approved visual direction is the dragon-monument plaza, layered imperial architecture, market waterways, forge quarter, guild court, teleport pavilion and garden/training approach.

This is a **machine-readable content manifest**, not a client DMap or a playable redesign. It is intentionally coordinate-free until a legally obtained patch-5065 Twin City map has been loaded and its collision/walkability grid verified. Never guess coordinates or write SQL directly against an unknown 5065 NPC schema.

## Concrete integration order

1. Obtain an authorized patch-5065 `GameMap.ini` and referenced `.DMap`, preserving the original assets privately and not adding them to GitHub.
2. Run the `tools/twin_city_preflight.py` validator against the manifest, and (when supplied) `GameMap.ini` plus the local game asset root. Validation does not redistribute assets.
3. Determine reliable x/y dimensions, passability, bridge edges, NPC interaction radii, safe spawns, and travel triggers from the real map; record verified positions in the manifest.
4. Build or commission **original** isometric terrain/object tile art from the concept. The concept illustration is not executable scene geometry. Create sprites/scene records/minimap, preserve correct footpoint/occlusion and draw-order behavior.
5. Revise the original walkability, scenery and portal links in compatible editor format; verify checksums and client/server agreement.
6. Implement server NPC actions and daily quests with persistence and silver-only rewards; guard claims against replay and preserve original service access.
7. Test actual game-client login, Twin City entry, path traversal and map transitions, save/relog, and graphics performance.

**Classic mechanics remain:** only five classic classes, one rebirth, silver only, no CP/mall. Extra token currencies are deferred; the dailies use silver for the first playable release.

## Distinct districts

- Dragon Plaza: central safe hub, services and the twin-dragon monument.
- Lotus Market: compact merchants, garments, accessories, canals and bridges.
- Ember Forge: smithing and repair quarter.
- Banner Court: guild services, ceremonial palace approach.
- Adventure Gate: beginner progression, route to hunting.
- Jade Waystation: travel and Job Center passage.

The content manifest declares **14 service slots, one proposed Job Center destination and three proposed quest hooks**. No proposed NPC spawn should be activated until tested in-game.

## Source constraints

COPS `MapManager::loadData()` expects `./GameMap.ini` sections `[Map1002]` with a `File` key. `MapData::load()` opens the referenced DMap. The DMap reader uses header dimensions, per-cell access flags and row checksums. Merely inserting a `map` SQL row or drawing concept art does not load geometry. See `src/Map/mapmanager.cpp` and `src/Map/mapdata.cpp` in the public upstream COPS source.

## Release gates

The manifest's `releases` fields stay false until evidence exists. No public ports or playable claim without a real compatible client, collision-tested city resources, authenticated world entry, character saving and security review.
