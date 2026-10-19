# Classic 5065 mechanics research — v0.8.0

**Status:** evidence register and implementation requirements; not a complete verified reconstruction. Date: 2026-10-19. All unverified formulas must stay configurable and must not be treated as official.

## The version boundary matters

- TQ official announcement dated **2008-09-16** identifies patch **5065**. It states that changes to PK equipment detainment, **composition points**, arrow quiver auto-reloading and some client fixes were **previews** of patch 5066, not proof they existed in 5065. [S1]
- TQ announced **5066** on **2008-09-19**, activating the revised PK and composition rules (scheduled activation on September 22). Do **not** silently back-port these if reconstructing pure 5065. [S2]
- TQ announced **Ninja** in **5089**, dated **2008-12-19**. It is out of scope and server-side creation/rebirth must reject it. [S3]
- COPS v7 targets 5065, but its README explicitly describes incomplete NPC and screen systems, and missing general functionality. [S4]
- Modern official guides can describe features added after 5065. Use them as **secondary hints**, not authoritative 5065 definitions. A modern private 5065-style server is not evidence of unchanged 2008 formulas. [S5][S6]

## Server design decisions already specified by project owner

| Rule | Server implementation contract | Evidence status |
|---|---|---|
| Classes | Trojan, Warrior, Archer, Water Taoist, Fire Taoist (Taoist's two specializations); reject Ninja and later classes for creation, promotion, rebirth, spell and item restrictions | Project rule; Ninja chronology [S3] |
| Rebirth | Exactly zero or one rebirth; atomic transition; validate current class/level/quest/item costs before commit | Project override; modern official FAQ confirms multiple rebirths existed, so NOT historical 5065 parity [S7] |
| Currency | No Conquer Points balance, sales, redemption, gift, mall, or CP-backed systems; silver / drops may be used based on documented rules | Project override; official 5065->5066 changes show CP-linked detainment, which is incompatible with our project [S1][S2] |
| Cosmetics | Custom garments/accessories as cosmetic entitlements, no invisible combat bonuses without explicit approved item stats and client asset review | Custom feature; no official 5065 formula asserted |
| Daily quests | UTC-day or configured reset-zone calendar chosen once; server-side transaction and unique claim; reward and claim in **same** database transaction | Custom feature; design requirement |

## Mechanics inventory and evidence gaps

| System | Known baseline | Not yet verified; source of truth needed |
|---|---|---|
| Character/account | COPS reports character create/load/save | Field defaults, class IDs, valid names, level EXP curve, promotion quests, starter gear, disconnect save ordering [S4] |
| Rebirth | Official FAQ describes first rebirth level 120, Water Taoist level 110; has several variants in later guide | Date-specific 5065 state of prerequisites, stat distribution, skills retained, rebirth items and transformations; server implements one only [S7] |
| Movement/world | COPS reports walk/jump/portals and DMap loading | Map IDs, coordinates, stamina costs, jump timing/range, terrain collision, teleport permissions and anti-speed rules [S4] |
| Combat | Physical/magic damage, dodge, attack speed, skill-specific effects known as categories | **Exact 5065** damage formulas, min/max ranges, magic resistance, reflect, criticals, XP skills, PvP scaling, level effects, cooldowns, line-of-sight; must validate from period sources/test vectors |
| Items/equipment | COPS reports vendor buy/sell, repair, consumables, equip | Patch-specific item tables, quality, durability, binding, upgrade probability, +item composition BEFORE 5066, socket/gem rates; later guides are not sufficient [S4][S2][S8] |
| Economy | Silver and item trade are required for classic play | Silver income/sinks, stack limits, vendor pricing, trade confirmation semantics; no CP routes |
| PK | PK modes / red-black status evidenced in official guides | Period-accurate score decay, kill penalties and drop rules. **Do not use post-5066 CP detainment** as 5065 truth [S9][S1][S2] |
| NPCs/quests | COPS Lua scripting / incomplete NPC interactions | Complete dialogue, quest item requirements, triggers, rewards, anti-replay, special maps, location rules [S4] |
| Social | Teams, guilds, trade, chat are part of classic design | Guild ranks/promotion, team loot/EXP distribution, marriage, warehouses, friends, PK teams: 5065 specifics not confirmed |
| Monsters/drops | COPS generator claims compatibility with official spawns | Spawn tables, respawn periods, AI, aggro, drop weights, level ranges, EXP and money rates [S4] |
| Network/security | COPS mentions TQ cipher, Blowfish, RC5, Diffie-Hellman | Exact packet schemas and authentication handshake for 5065; interoperability, key lifecycle, replay protection, length checks, authorization [S4] |
| Custom content | Maps, city NPCs, garments, accessories, daily quests requested | Version-specific asset formats and authorized asset provenance; transaction idempotency; rollback and compatibility |

## What NOT to transplant

- 5066 composition-point formula (even though some archived 'composition' guides present it as universal); source [S2][S8].
- 5066 CP equipment detainment; conflicts with both 5065 period and project's no-CP rule [S1][S2].
- Ninja 5089+, later classes, mounts, refinery/purification or modern itemtype.dat layouts without version verification [S3][S10].
- Second rebirth or reincarnation even if present in later official guides [S7].

## Confidence codes

**Confirmed-era:** 2008 official dated patch release and chronology. **Confirmed-codebase:** specifically advertised in COPS README but not verified via a compiled game. **Project override:** owner-specified rule, not history. **Unverified:** formulas/assets/packet fields pending primary documents and reference captures. Do not label unverified as bug-free implementation-ready.

## Research and acceptance approach

1. Pin exact client archive hash (SHA-256), COPS commit hash and licenses. Keep proprietary assets out of repository.
2. Inventory COPS tables and packet handlers. Record missing code paths and date-sensitive mechanics, annotated with source and commit/file lines.
3. Capture authorized client behavior on a controlled test realm. Convert each mechanic to reproducible input/output fixtures (including edge cases).
4. Implement deterministic C++ unit tests, property tests and integration tests; golden tests for damage, XP, items, movement, economy and persistence.
5. Require exploit tests and production operational checks in `SECURITY-TEST-MATRIX.csv` before any public hosting.

## Sources (URLs and applicability)

- [S1] TQ official 5065 release (2008-09-16): https://co.99.com/content/2008-09-16/20080916180652547.shtml
- [S2] TQ official 5066 change notice (2008-09-19): https://co.99.com/content/2008-09-19/20080919012428607.shtml
- [S3] TQ official 5089 Ninja launch (2008-12-19): https://co.99.com/content/2008-12-19/20081219015941741.shtml
- [S4] COPS v7 repository / README: https://gitlab.com/conquer-online/servers/cops-v7-emulator and https://github.com/cptsky42/COPS-v7-Emulator
- [S5] Independent, modified preservation realm (NOT official 2008 behavior): https://playconqueronline.com/
- [S6] Later general documentation index: https://www.conqueronline.com/guide/faqs.shtml
- [S7] Later official rebirth FAQ: https://www.conqueronline.com/guide/faqs.shtml
- [S8] Official composition guide (includes composition-points modernized system, verify publication/version separately): https://co.99.com/content/2008-08-28/20080828233420444.shtml
- [S9] Official PK interface: https://co.99.com/guide/guides/pkint.shtml (publication/date not verified)
- [S10] Client file guide documents ItemType.dat in patch 5517 only, **NOT 5065**: https://github.com/conquer-online/wiki/blob/main/src/files/content/itemtype.dat.md

## Secondary reference: Classic Conquer Wiki
https://wiki.conqueronline.net/ is a modern community-server wiki. Use it as a feature inventory and candidate mechanic reference only; independently verify all rules against patch 5065. Do not import VIP, second rebirth, or other custom-server features into our one-rebirth, no-CP ruleset.
