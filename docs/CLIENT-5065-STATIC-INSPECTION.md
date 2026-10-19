# Client 5039 + 5065 patch: safe inventory and extraction procedure

User-provided archive: `Conquer_v5039.exe` (about 456 MB) and patch `5065.exe` (about 716 KB); historical patch bundle `enzf_5000_5999.rar` on Drive (about 1.39 GB).

**No code in this repository runs these executables.** `tools/inspect_legacy_installer.py` computes SHA-256, checks DOS/PE headers, scans a few self-extracting archive markers and optionally asks 7-Zip to **list** contents without unpacking or executing. A successful file listing is not malware clearance.

A patch labeled `5065` is a **target version**, not proof it can update a 5039 client directly. Determine documented `from` versions and dependencies from each patch's metadata before applying any patch. Never assume 5039 -> 5065 in one operation.

## Inspection

On a trusted Windows machine with a maintained 7-Zip installation, run:

```powershell
py -3 tools/inspect_legacy_installer.py "D:\\Downloads\\Conquer_v5039.exe" --output base-client-inventory.json
py -3 tools/inspect_legacy_installer.py "D:\\Downloads\\5065.exe" --output patch-5065-inventory.json
```

Inspect output before attempting anything else. Do not run installers as administrator, disable antivirus, or allow unknown auto-updaters to connect. Avoid placing executable/game resources in public repositories or public artifact uploads.

## Map asset checks after authorized extraction

Find `GameMap.dat`, `GameMap.ini`, `*.DMap`, scene resources and original minimap art. **Do not guess that the asset filename is `1002.DMap`**: COPS loads map 1002 using the `[Map1002]` section's `File` reference.

Run `python tools/twin_city_preflight.py content/twin_city/twin_city_reimagined_v1.json --gamemap-ini <path> --asset-root <root>` once the actual map files are present. This only validates the local header and a map reference; full rendering/collision tests are still necessary. The concept image cannot become geometry without tile/scene creation.

Before running any unknown binary, antivirus scan, inspect certificate provenance, and isolate experimental analysis on a disposable test machine.


## Verified 5065.exe binary findings (2026-10-19)

The user-supplied 5065.exe was read directly from the connected Google Drive, without execution, and inspected in memory. The file is 715,595 bytes. The DOS/PE magic is valid, its PE machine value is 0x014c (32-bit x86), and PE resource strings explicitly identify a **WinRAR SFX**. A RAR4 archive begins at byte offset 103424. Its entry headers were parsed read-only, without executing or unpacking payloads.

There are **172 archive entries** including 32 .c3 effects, 88 .dds textures, 50 directory entries, one .dat and one .htm file. The records include interface/gear effects. The only filename matches to "Map" were a `data\\MapItemIcon` directory and icon texture; **no .DMap or GameMap.ini entries exist in this patch payload**. It is not a Twin City geometry provider. Header enumeration does not imply safety, authenticity or compatibility.

Next: inspect the larger 5039 installer to locate its bundled map resources; do not publish proprietary assets or run the SFX. The CI downloader is supplementary and must not be taken as a client playability test.
