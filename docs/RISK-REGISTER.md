# Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Candidate C++ source is incomplete | High | Audit before adoption; do not mistake protocol demos for a playable server |
| Client/server patch mismatch | High | Lock one patch only after compatibility testing |
| Unclear rights to client assets or source | High | Review licenses and permissions before distribution or public hosting |
| Hidden CP/mall paths remain | High | Search handlers, commands, rewards, shops, and database procedures; test server-side |
| Duplicate daily quest rewards | High | Atomic transaction, unique completion key, replay/duplicate-packet tests |
| Custom items crash or display incorrectly | Medium/High | Validate IDs and asset references; test client and server together |
| Google Drive unavailable to ChatGPT | Medium | Generate artifacts here; user uploads to Drive or enables an approved integration |
| Secrets leak into source control | High | Example configs only; secrets supplied locally and excluded from Git |
| "Bug-free" treated as guarantee | High | Define tests, known issues, release gates, monitoring, and rollback |

## Scope note
This plan assumes a private, authorized development environment. It does not include proprietary client assets or claim affiliation with TQ Digital.
