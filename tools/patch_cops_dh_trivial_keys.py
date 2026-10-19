#!/usr/bin/env python3
"""Reject degenerate Diffie-Hellman public keys before exponentiation in COPS."""
from pathlib import Path
import sys

def patch(root):
    p=Path(root)/"src/Network/msgloginchallenges.cpp"
    s=p.read_text(encoding="utf-8")
    old="""    DiffieHellman& exchange = client.getExchange();
    string s_key = exchange.handleResponse(b_key);
    SAFE_DELETE_ARRAY(b_key);"""
    new="""    // A public DH value of zero or one yields a predictable session key.
    // Ignore leading zeroes before testing, rather than allowing "0001".
    // This is a minimum safeguard; a full group/subgroup validation is
    // required before treating legacy DH as secure for public deployment.
    size_t first = 0;
    while (first < static_cast<size_t>(b_len) && b_key[first] == '0')
        ++first;
    if (first == static_cast<size_t>(b_len) ||
        (first + 1 == static_cast<size_t>(b_len) && b_key[first] == '1'))
    {
        SAFE_DELETE_ARRAY(b_key);
        client.disconnect();
        return;
    }

    DiffieHellman& exchange = client.getExchange();
    string s_key = exchange.handleResponse(b_key);
    SAFE_DELETE_ARRAY(b_key);"""
    if s.count(old)!=1:
        raise RuntimeError("COPS DH input anchor changed")
    p.write_text(s.replace(old,new),encoding="utf-8")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: patch_cops_dh_trivial_keys.py <cops-source>")
    patch(Path(sys.argv[1]))
