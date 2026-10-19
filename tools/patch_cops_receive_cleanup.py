#!/usr/bin/env python3
"""Correct COPS receive cleanup on truncated post-key-exchange packet tails."""
from pathlib import Path
import sys

def patch(root):
    p=Path(root)/"src/server.cpp"
    source=p.read_text(encoding="utf-8")
    # This anchor applies AFTER tools/patch_cops_bounds.py.
    old="""            default:
                {
                    if (aLen < sizeof(Msg::Header))
                        return;

                    client->getCipher().decrypt(received, aLen);"""
    new="""            default:
                {
                    if (aLen < sizeof(Msg::Header))
                    {
                        // A trailing partial packet after DH exchange is not
                        // supported until encrypted TCP reassembly exists.
                        // Free the owned temporary buffer before disconnecting.
                        SAFE_DELETE_ARRAY(received);
                        aClient->disconnect();
                        return;
                    }

                    client->getCipher().decrypt(received, aLen);"""
    if source.count(old)!=1:
        raise RuntimeError("COPS receive cleanup anchor mismatch")
    p.write_text(source.replace(old,new),encoding="utf-8")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: patch_cops_receive_cleanup.py <cops-checkout>")
    patch(Path(sys.argv[1]))
    print("Patched truncated encrypted frame cleanup")
