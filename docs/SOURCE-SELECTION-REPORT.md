# Source-selection report — 2026-10-19

## Executive decision

**Do not adopt a server source as production-ready yet.** The public-source audit found no verified, complete, maintained C++ Conquer Online server that already satisfies the requested feature set. The best C++ research candidate located is COPS v7 for patch 5065, but its own README says many features are not implemented or completed. It must be treated as an incomplete base, not a working server.

**Recommended working target for the next audit:** patch 5065, conditional on a source/license/build audit and a compatible client being available. This is a pragmatic research target, not a claim that it is the best or newest client.

## Candidate assessment

### 1. COPS v7 Emulator — C++ / Qt, patch 5065
Repository: https://gitlab.com/conquer-online/servers/cops-v7-emulator
Evidence: https://github.com/cptsky42/COPS-v7-Emulator

Documented strengths:
- C++ implementation with Qt 4/5.
- MySQL-oriented data model.
- TQ custom cipher and other security/protocol components.
- Map/DMap loading, Lua scripting, character creation/loading/saving, movement, portals, and some item/NPC functionality.

Documented weaknesses:
- The README explicitly calls it a base source and says most functionalities are not implemented or completed.
- NPC interactions and screen system are marked incomplete.
- The project was developed in 2013–2014 and will likely require toolchain/dependency modernization.
- A successful compile would not prove that client login, world entry, or core gameplay work.

Verdict: **Best C++ server candidate found, but high risk.** Audit source and license, build in isolation, and test against a legally obtained matching client before committing.

### 2. Comet — C# / .NET, multiple patch branches
Repository: https://github.com/conquer-online/comet

Documented strengths:
- Multiple patch branches, including 4294, 4343, 5017, 5065, and 5187.
- Useful patch and protocol reference.
- Separates account and game servers and provides setup documentation.

Documented weaknesses:
- Not C++; the README calls it a skeleton with no gameplay features beyond login.

Verdict: **Reference only** under the current C++ requirement. Useful for patch comparisons and protocol understanding, not a drop-in server.

### 3. Dragon — C++ client launcher/injection framework
Repository: https://github.com/conquer-online/dragon

The repository README describes a launcher/injector and client modules for connection redirection and related client behavior. It is not a game server.

Verdict: **Exclude as server foundation.** Potentially relevant only if client-side tooling is later needed and its license/usage are reviewed.

### 4. COPS serverless — C++ DLL, patch 4330
Repository: https://github.com/conquer-online/cops-serverless

The community organization describes this as a custom DLL mimicking an in-process server and targeting version 4330. This is not the conventional standalone account-server/game-server architecture desired for the project.

Verdict: **Not preferred** for the planned standalone server.

## Why not choose the newest patch immediately?

Later patches introduce more client/protocol complexity and additional game systems. The project specifically excludes Ninja and later classes and removes CP/mall functionality. A newer client may be possible, but only if a C++ server implementation supports that patch or the cost of porting is accepted. Comet's patch table identifies 5187 as the patch that adds Ninja and other systems, but Comet itself is C# and login-only.

## Proposed decision gate

Before adopting COPS v7 or any alternative:

1. Read the full license and note obligations for modification/distribution.
2. Clone an exact commit and record its hash.
3. Inventory source modules, dependencies, build system, database schema, and client data expectations.
4. Build from a clean checkout using documented dependencies.
5. Start the processes and capture logs.
6. Test matching-client login, character creation, world entry, movement, map transitions, NPC dialogue, combat, inventory, save/restart.
7. Record every failure and missing feature.
8. Only then decide whether to extend this source or pivot.

**No client binaries or copyrighted game assets are included in this project package.** Use only client files and assets you are authorized to access and use.

## Feature strategy once a base is selected

- Supported class IDs should be an explicit allowlist, enforced on character creation and every class-change path.
- Rebirth must be enforced server-side: first rebirth allowed under configured rules; second rebirth rejected.
- CP and shopping mall must be disabled in server handlers and economic paths, not just hidden in the client.
- NPCs, quest definitions, item metadata, and balance settings should be data-driven.
- Daily quest rewards must be transactional and idempotent to prevent duplicate grants.
- Custom garments and accessories require both server-side item definitions and compatible client-side visual assets; server code alone cannot create missing sprites/animations.
- Map/city changes depend on the selected client map format, collision files, portals, spawns, and client assets.

## References

- COPS v7 README: https://github.com/cptsky42/COPS-v7-Emulator/blob/master/README
- COPS v7 GitLab project: https://gitlab.com/conquer-online/servers/cops-v7-emulator
- Comet README: https://github.com/conquer-online/comet
- Conquer Online development organization: https://github.com/conquer-online
- Dragon README: https://github.com/conquer-online/dragon
- COPS serverless: https://github.com/conquer-online/cops-serverless
