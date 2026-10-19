# Patch 5065 client acquisition status

Source: https://tqarchive.org/, listing historical English Conquer client 5039 and patches 5000–5999. The first-party official site currently supplies much newer clients, not a verified 5065 build.

The private CI inventory job reads public Internet Archive **metadata only**:
- https://archive.org/details/conquer-online-v5039
- https://archive.org/details/conquer-patches-5000-5999

Its output contains filename, archive-declared size, SHA-1/MD5, and source description; these are **not** independent cryptographic attestations. The workflow does not execute installers, fetch client archives, rehost proprietary assets, apply unknown executables or commit assets to GitHub. Historical files must be treated as untrusted until local malware scanning and manual inspection.

Before claiming a compatible 5065 client: obtain permitted assets, verify a complete patch chain, inspect each patch, hash obtained files, avoid running patch launchers as administrator, and extract GameMap.ini / map 1002 DMap and scene data for a local inventory. Downloading an archive is not equivalent to having modification/redistribution permission.

Do not claim playability until actual COPS login/character/world entry passes.
