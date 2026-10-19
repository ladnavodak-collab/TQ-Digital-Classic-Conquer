#!/usr/bin/env python3
"""Send truncated pre-login fragments to LOCAL COPS listeners only."""
import socket
import time
import argparse
from tools.cops_loopback_session_probe import probe, connect

def run():
    # 1-byte input cannot contain a COPS packet header and must disconnect.
    for port in (9958,5816):
        for _ in range(3):
            with connect(port) as sock:
                sock.settimeout(2)
                if port==5816:
                    if not sock.recv(4096):
                        raise RuntimeError("No initial game prelogin challenge")
                sock.sendall(b"\\x01")
            time.sleep(0.08)
    result=probe(2)  # Must still accept fresh clients and emit challenges.
    print("PASS: COPS survived 6 truncated pre-login packets",result,flush=True)

if __name__=="__main__":
    run()
