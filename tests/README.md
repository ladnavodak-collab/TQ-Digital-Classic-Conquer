# Initial test strategy

The scaffold currently has no game-server tests because it implements no game protocol or mechanics.

First required test categories after source selection:
- Build from clean checkout
- Config parsing and invalid-config rejection
- Login and authentication failure handling
- Character creation and class allowlist
- Rebirth limit (0 -> 1 permitted; 1 -> 2 rejected)
- CP/mall request rejection and no alternate CP grant/spend paths
- Inventory transaction atomicity and item duplication attempts
- NPC dialogue and teleport target validation
- Daily quest progress, reset boundary, duplicate completion and reward replay
- Restart persistence and backup restoration
- Malformed packet length and unknown message handling
