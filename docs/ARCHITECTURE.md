# Proposed architecture

This is a target architecture, not a description of an existing server.

## Layers
1. **Network/session layer** — sockets, framing, encryption, packet parsing, rate limits.
2. **Protocol adapter** — patch-specific packet layouts and message handlers; no game rules here.
3. **Application services** — authentication, character selection, world entry, inventory, quests.
4. **Domain/game systems** — combat, movement, skills, items, classes, rebirth, drops, economy.
5. **Content providers** — maps, NPCs, monsters, item definitions, dialogue, quest definitions.
6. **Persistence** — accounts, characters, inventory, quest state, audit events.
7. **Operations** — structured logs, configuration, health checks, backups, metrics.

## Important boundaries
- Never trust client-reported damage, item grants, quest completion, or currency changes.
- Validate all packet sizes and fields before reading them.
- Use database transactions for item movement, rewards, and character saves.
- Make daily quest completion idempotent: duplicate packets must not grant duplicate rewards.
- Use a server-side daily reset policy and document its timezone.
- Keep protocol-specific code isolated so a patch change does not require rewriting quest logic.
- Keep secrets out of source control; provide an example config only.

## Classic ruleset
- Explicit allowlist of supported classes for the chosen patch.
- Reject unsupported class IDs on character creation and all later class-change paths.
- One rebirth maximum, enforced server-side and covered by tests.
- CP and shopping mall systems disabled at the service/handler level, not merely hidden in UI.
- Define a replacement currency/reward policy before disabling any existing acquisition or spending paths.

## Content data
Proposed entities:
- `npc_definition`: id, name, map, coordinates, script/dialogue key, enabled
- `quest_definition`: id, title, description, objective type, target, count, reward, reset policy, enabled
- `quest_progress`: character id, quest id, reset period, progress, completion timestamp
- `item_definition`: id, name, type, level/quality requirements, stats, icon/asset references
- `map_definition`: id, name, file references, spawn rules

These are conceptual schemas. Exact columns must follow the chosen source and database.

## Operations
- Separate development, test, and production configuration.
- Structured logs with timestamps and severity.
- Automated backup and restore verification.
- Version-controlled schema migrations.
- A release checklist and rollback plan.
