# Decision log

## D-001 — Language
**Decision:** C++ is the required server language.
**Status:** Accepted.

## D-002 — Target patch
**Decision:** Do not lock a patch until 4294 and 5065 have been compared against the available source and client assets.
**Status:** Open.
**Reason:** The client protocol, packet layouts, encryption, data files, and content differ by patch.

### Candidate A: 4294
- Pros: classic Conquer 2.0 feel; predates Ninja and later class systems.
- Unknowns: availability of a maintainable, sufficiently complete C++ server foundation; exact client assets and protocol requirements.
- Decision gate: demonstrate a buildable source base and a documented path to login/world entry.

### Candidate B: 5065
- Pros: still predates the 5187-era Ninja feature set; protocol documentation and community projects exist.
- Risks: COPS v7 is C++/Qt but explicitly incomplete; a playable 5065 emulator in another language does not satisfy the C++ requirement.
- Decision gate: audit COPS v7 and any other legally usable C++ candidate before adoption.

## D-003 — COPS v7
**Decision:** Research candidate only; not approved as production foundation.
**Reason:** Its README says many functionalities are not implemented or completed.
**Reference:** https://gitlab.com/conquer-online/servers/cops-v7-emulator

## D-004 — Comet
**Decision:** Use as patch/protocol reference only unless the language requirement changes.
**Reason:** Comet is C#, not C++.
**Reference:** https://github.com/conquer-online/comet

## D-005 — Persistence
**Proposed:** MariaDB/MySQL if compatible with the selected codebase and deployment constraints.
**Status:** Provisional. Database choice follows source/dependency audit.

## D-006 — Content authoring
**Proposed:** Keep quests, NPC dialogue, item definitions, and balance values in versioned data files or database tables rather than scattering them through code. Use schema validation and migration scripts.
**Status:** Accepted as architectural direction.

## D-007 — Source audit (2026-10-19)
**Finding:** No verified complete C++ server meeting the full project requirements has yet been established. COPS v7 / 5065 is the strongest C++ server candidate found, but it is explicitly incomplete. See `SOURCE-SELECTION-REPORT.md`.
**Next gate:** Audit license, dependencies, clean build, and actual client interoperability before adoption.
