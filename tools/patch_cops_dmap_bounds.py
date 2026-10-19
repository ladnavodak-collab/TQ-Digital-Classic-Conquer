#!/usr/bin/env python3
"""Harden upstream COPS v7 DMap parser against malformed map geometry."""
from pathlib import Path
import sys

def replace_once(path, before, after):
    source=path.read_text(encoding="utf-8")
    if source.count(before)!=1:
        raise RuntimeError(f"upstream DMap anchor mismatch ({source.count(before)}): {path}")
    path.write_text(source.replace(before,after),encoding="utf-8")

def patch(root: Path):
    path=root/"src/Map/mapdata.cpp"
    replace_once(path,
        """        if (width < UINT16_MAX && height < UINT16_MAX)
        {
            mWidth = (uint16_t)width;
            mHeight = (uint16_t)height;
        }""",
        """        // Reject zero dimensions and oversized inputs before allocating cells.
        // The 16-million-cell budget limits memory/CPU abuse by corrupt DMaps.
        if (width > 0 && height > 0 && width < UINT16_MAX &&
            height < UINT16_MAX && uint64_t(width) * height <= 16000000ULL)
        {
            mWidth = (uint16_t)width;
            mHeight = (uint16_t)height;
        }""")
    replace_once(path,
        """    mCells = new Cell[mWidth * mHeight];""",
        """    if (err != ERROR_SUCCESS)
        return err;
    mCells = new Cell[size_t(mWidth) * size_t(mHeight)];""")
    replace_once(path,
        """    DOIF(err, aReader.readInt32(count));
    mPassages.reserve(count);""",
        """    DOIF(err, aReader.readInt32(count));
    if (err != ERROR_SUCCESS)
        return err;
    if (count < 0 || count > 100000)
        return ERROR_BAD_LENGTH;
    mPassages.reserve(size_t(count));""")
    replace_once(path,
        """            if (posX < UINT16_MAX && posX < UINT16_MAX)""",
        """            if (posX < mWidth && posY < mHeight)""")
    replace_once(path,
        """    LOG(INFO, "Found %d layers for the map.", count);

    for (int32_t i = 0; ERROR_SUCCESS == err && i < count; ++i)""",
        """    if (err != ERROR_SUCCESS)
        return err;
    if (count < 0 || count > 100000)
        return ERROR_BAD_LENGTH;
    LOG(INFO, "Found %d layers for the map.", count);

    for (int32_t i = 0; ERROR_SUCCESS == err && i < count; ++i)""")
    replace_once(path,
        """                size_t posX = ((startX + sceneOffsetX) + x) - width;
                                size_t posY = ((startY + sceneOffsetY) + y) - height;
                                if (posX < UINT16_MAX && posX < UINT16_MAX)""",
        """                // Use a wide signed intermediate to avoid unsigned wrap.
                                int64_t posX = int64_t(startX) + sceneOffsetX + x - width;
                                int64_t posY = int64_t(startY) + sceneOffsetY + y - height;
                                if (posX >= 0 && posY >= 0 &&
                                    posX < mWidth && posY < mHeight)""")
    replace_once(path,
        """                if (Finder::fileExists(fileName))""",
        """                // Binary map filenames are fixed-size byte fields and may
                // have no terminating NUL. Fail before strlen/log/file access.
                if (err == ERROR_SUCCESS && !memchr(fileName, 0, sizeof(fileName)))
                    return ERROR_BAD_LENGTH;
                if (err == ERROR_SUCCESS && Finder::fileExists(fileName))""")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: patch_cops_dmap_bounds.py <upstream-source-dir>")
    patch(Path(sys.argv[1]))
    print("Applied DMap allocation, passage, layer, and scene-coordinate guards.")
