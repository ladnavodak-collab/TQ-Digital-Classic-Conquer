#!/usr/bin/env python3
"""Allow a standalone completed DH frame without dropping a valid game session."""
from pathlib import Path
import sys

def patch(root):
    path=Path(root)/"src/server.cpp"
    text=path.read_text(encoding="utf-8")
    before="""                    aLen -= len;
                    memcpy(received, ptr, aLen);"""
    after="""                    aLen -= len;
                    // A valid DH response commonly arrives without an
                    // encrypted game message in the same TCP read. Preserve
                    // the negotiated session instead of falling through
                    // to the short-packet disconnect guard.
                    if (aLen == 0)
                    {
                        SAFE_DELETE_ARRAY(received);
                        return;
                    }
                    memcpy(received, ptr, aLen);"""
    if text.count(before)!=1:raise RuntimeError("DH zero-tail COPS anchor mismatch")
    path.write_text(text.replace(before,after),encoding="utf-8")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: patch_cops_dh_zero_tail.py <upstream-checkout>")
    patch(Path(sys.argv[1]))
    print("Keep valid DH-only session open for subsequent MsgConnect")
