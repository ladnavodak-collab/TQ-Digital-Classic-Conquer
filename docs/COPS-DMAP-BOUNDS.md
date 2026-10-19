# COPS v7 map parser hardening

The COPS original DMap parser is unsafe on malformed/untrusted client-supplied or locally obtained map files. In particular, it checks posX twice when reading passage coordinates and 2D terrain overlays, enabling an out-of-range Y index; it reserves a signed passage count without validating negativity; and it allocates cells from untrusted header dimensions.

`tools/patch_cops_dmap_bounds.py` applies these changes to a disposable upstream checkout:

- Requires map width and height to be nonzero, fit the existing 16-bit coordinates, and total no more than **16 million cells**; rejects bad dimensions before allocating.
- Rejects negative or over-100,000 passage and layer counts, and checks read errors before allocating.
- Bounds passage locations to loaded map width/height, not merely `UINT16_MAX`.
- Computes scene overlay coordinates using 64-bit signed math and rejects negative/out-of-bounds X/Y before indexing the cell grid.
- Requires NUL terminator inside the fixed-length terrain scene filename before passing it to C string APIs.

These bounds may reject unusually large or broken official custom maps until validated against permitted data. This is a security/robustness patch, **not** a working 5065 map loader, installer, or playable world. Upstream license and attribution must be preserved. Qt5 build is required to prove compatibility; unit tests alone verify only source transformation.
