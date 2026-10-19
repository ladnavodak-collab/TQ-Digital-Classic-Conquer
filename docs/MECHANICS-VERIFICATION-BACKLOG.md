# Mechanics verification backlog

No individual mechanic is deemed 5065-accurate until we have **source, implementation, and a passing reference fixture**.

## Gate A — Source acquisition
- [ ] COPS v7 archived upstream exact commit and license reviewed
- [ ] Build without modifying tracked original sources; archive compiler and dependency logs
- [ ] Legitimately obtained version-5065 client asset hash recorded (no client binaries included in project package)
- [ ] Compare `itemtype`, skill, leveling and map data by version and license

## Gate B — Required original behavior
- [ ] Character creation, stat caps, first rebirth, promotions
- [ ] All classic spells: range, timing, effects, XP skills, prerequisites
- [ ] Equipment stats, sockets, gems, upgrades, durability, repair, silver
- [ ] HP/MP, attack, magic, accuracy, dodge, defense, PK, death/respawn
- [ ] Walk, jump, stamina, terrain, portals, map flags, monster AI/drops
- [ ] Team, trading, chat, guild, NPCs, warehouse and save/restart

## Gate C — Project-specific differences
- [ ] One rebirth max enforced in database AND all service paths
- [ ] No Ninja/later class values in character mutation, items, skill casts, admin, scripts
- [ ] No CPs or shopping mall including inbound packets, NPC scripts and database fields
- [ ] Custom garments/accessories and city modifications version-compatible
- [ ] Daily quests reward exactly once and withstand server restarts

## Gate D — Release blockers
- [ ] Every P0 case in SECURITY-TEST-MATRIX.csv passes
- [ ] Security review of authentication, packet parsing, secrets, logging, database roles and admin controls
- [ ] Multi-client soak/stress test, backup restore drill, rollback plan, crash recovery
- [ ] Local/private test on Windows 11 BEFORE opening public ports

**Blocker:** At this point no working 5065 client/server exchange has been verified in our project. A clean CMake build tests only the foundation modules, not COPS or the live game.
