# COPS v7 empty database loader contract

This project now has an **intentionally empty and incomplete** MariaDB test schema at `db/ci_loader_schema.sql`. It permits validation of the six startup loader `SELECT` statements and the nine explicitly selected map columns against the pinned (when available) upstream source.

The empty schemas for itemtype, npc, monstertype, generator and magictype contain only an `id` placeholder. They must never be populated or treated as production definitions without reviewing upstream field-by-index contracts.

**No actual map data, collision maps, monsters, NPC interactions, character or account persistence schema, original game assets, or 5065 compatibility is included.** In particular, zero rows in `map` do not make Twin City available; never call this a playable environment.

CI checks the exact COPS loader queries via `tools/cops_schema_contract.py` and uses disposable MariaDB with least-privilege credentials for SQL `SELECT` smoke tests. Do not copy the schema to an existing server database. Real schema work requires audited data definitions and permitted game data.
