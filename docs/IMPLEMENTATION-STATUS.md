# Implementation status — v0.3.0

## Implemented and tested
- Standalone C++17 classic rules library.
- Explicit class allowlist: Trojan, Warrior, Archer, Fire Taoist, Water Taoist.
- Ninja and later classes rejected by this policy.
- Rebirth policy allows only characters with zero prior rebirths to rebirth once.
- CP and mall policy flags disabled.
- In-memory daily quest claim deduplication keyed by character, quest, UTC date.
- Automated CTest suite covering allowed/forbidden classes, rebirth limits, CP/mall flags, and duplicate claims.

## Not implemented / important limitations
- Rules are not wired into a login server, packet handlers, or a game database.
- In-memory daily quest claims are lost on restart and are not safe for multiple workers; production requires transactional persistence and a database uniqueness constraint.
- No network server, character persistence, map runtime, NPCs, combat, item assets, compatible client, or real playable world yet.
- The COPS v7 repository was not cloned or built here because this runtime cannot resolve github.com; repository documentation was reviewed through web access only.
- Patch 5065 remains provisional until client/source compatibility and licensing are audited.

## Next engineering gate
Obtain a legally usable COPS v7 source snapshot and client build, verify license, pin commit, inventory dependencies and compile it in a reproducible environment. Then integrate the policy library at all relevant server validation points.
