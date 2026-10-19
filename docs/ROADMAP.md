# Development roadmap

## Phase 0 — Feasibility and source audit
Tasks:
- Compare client patches 4294 and 5065.
- Find candidate C++ source and inspect its license, history, dependencies, and completeness.
- Confirm client assets can be used lawfully.
- Build candidate source from a clean checkout.
- Document known missing systems and test the candidate client connection.

Exit criteria:
- Chosen patch and rationale recorded.
- Source builds reproducibly.
- Client can connect through login and reach a character/world if the candidate claims to support it.
- All limitations and third-party licenses documented.

## Phase 1 — Build and runtime baseline
Tasks:
- Reproducible CMake/build instructions or preserve the source project's own build system.
- Configuration validation and structured logs.
- Local development database and migration workflow.
- Startup/shutdown handling and crash diagnostics.

Exit criteria:
- Clean build from documented steps.
- Invalid config fails clearly.
- Server starts/stops repeatedly without corrupting data.

## Phase 2 — Core gameplay verification
Test login, character creation, movement, combat, skills, inventory, equipment, NPC interactions, drops, saves, reconnects, and restarts.
Do not rewrite working systems without a demonstrated defect.

## Phase 3 — Classic ruleset
- Remove unsupported later classes and class-change paths.
- Enforce one rebirth maximum server-side.
- Disable CP purchase/spend paths and mall handlers safely.
- Audit all reward, shop, trade, drop, and admin commands for unintended CP or item paths.

## Phase 4 — Content tools and custom content
- Data-driven NPC dialogue and placement.
- Daily quest definitions, progress, reset policy, reward transactions, anti-duplication tests.
- Custom item definitions and assets, with client compatibility checks.
- Map/city edits only after confirming map format, collision, teleport, and spawn data requirements.

## Phase 5 — Release hardening
- Test concurrent clients and reconnects.
- Validate malformed packets and permission boundaries.
- Backup/restore drill.
- Regression suite, release notes, known-issues list, rollback instructions.

## Definition of done
A feature is not complete merely because it compiles. It must have an acceptance test, failure-path checks, and a documented rollback path.
