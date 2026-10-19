# First runtime COPS startup probe (not playable)

The private `COPS disposable database and startup smoke` workflow compiles COPS v7 with the receive-bounds, DH-bounds, database configuration, and Argon2id verification patches.

It then creates a throwaway MariaDB instance with a restricted game application account and a generated credential, without writing that credential to GitHub or uploaded logs.

**Acceptance of this test**:
- The executable builds from actual COPS upstream source.
- It rejects missing SQL secrets at startup (fail closed).
- It can be run against a disposable database to observe the *next* failure.
- It prints whether either game listener was observed, but listener messages do not imply successful loading or authenticated gameplay.

The empty database does **not** include the original 5065 schema, game maps, `GameMap.ini`, or official game content. COPS attempts `loadAllMaps`, `loadAllItems`, `loadAllNPCs`, `loadAllMonsters`, `loadAllGenerators`, and `loadAllMagics`; therefore this is deliberately *not* an end-to-end server startup or client login test.

A real playable build still needs a vetted database migration, legitimate client/map resources, cipher-accurate encrypted TCP stream reassembly, real login and character persistence tests. Keep listeners inaccessible to public networks.

## Mandatory starter city check

The source-level startup gate now requires `MapManager::getMap(1002)` to return a loaded map **after** SQL/world loader success and **before** either listener binds. This closes a false-ready case where the `map` query returns zero rows but reports success. The check depends on the real game map, which must be registered from database map rows and a valid `GameMap.ini`/DMap mapping. It does **not** generate terrain, bypass missing assets, or prove gameplay.

The fail-closed check uses `ERROR_NOT_FOUND` and logs `Twin City map 1002 is not loaded`. The source patch test verifies the guard precedes both listener setup calls; upstream source and Qt compilation remain CI dependent.

## Integrated hardened COPS build

The database smoke workflow now also applies `tools/patch_cops_dmap_bounds.py` after the existing security patches and Twin City startup gate. It verifies the two guards exist in the upstream source before compiling the real COPS executable. This prevents testing one build variant while shipping incompatible individual hardening patches.

A green smoke test **does not** prove 1002 map loading: the disposable CI database and map assets are intentionally incomplete, so expected startup behavior is refusal to listen. Real map geometry, approved assets, character login and world-entry checks remain outstanding.
