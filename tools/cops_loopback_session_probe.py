#!/usr/bin/env python3
"""Exercise real COPS TCP accept/close and first game handshake on localhost only.

No login credentials, unknown packets, or encrypted messages are sent.
"""
import argparse
import socket
import time

ACCOUNT_PORT=9958
GAME_PORT=5816

def connect(port, timeout=2):
    return socket.create_connection(("127.0.0.1",port), timeout=timeout)

def probe(attempts=3):
    if not (1 <= attempts <= 20):
        raise ValueError("attempts must be in 1..20")
    result={"account_connections":0,"game_connections":0,"game_handshake_bytes":0}
    for _ in range(attempts):
        with connect(ACCOUNT_PORT):
            result["account_connections"] += 1
        # Server sends a Blowfish/DH login challenge on game-port connect.
        # Read only; do NOT guess crypto, transmit malformed packets, or claim authentication.
        with connect(GAME_PORT) as sock:
            sock.settimeout(3)
            data=sock.recv(8192)
            if not data:
                raise RuntimeError("game listener closed before sending exchange request")
            result["game_handshake_bytes"] += len(data)
            result["game_connections"] += 1
        time.sleep(0.12)
    # Make another connection AFTER multiple disconnect callbacks to catch crashes.
    with connect(ACCOUNT_PORT):
        pass
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--attempts",type=int,default=3)
    parser.add_argument("--wait-seconds",type=float,default=10)
    args=parser.parse_args()
    if not (0 < args.wait_seconds <= 60):
        parser.error("--wait-seconds must be in (0,60]")
    deadline=time.monotonic()+args.wait_seconds
    while True:
        try:
            with connect(ACCOUNT_PORT, timeout=0.3):
                pass
            with connect(GAME_PORT, timeout=0.3):
                pass
            break
        except OSError:
            if time.monotonic()>=deadline:
                raise SystemExit("FAIL: COPS account/game listeners not available on localhost")
            time.sleep(0.2)
    stats=probe(args.attempts)
    print("PASS: real COPS accepted and closed both loopback session types",stats,flush=True)
    print("The game-port bytes are a pre-login handshake, NOT an authenticated session.",flush=True)

if __name__=="__main__":
    main()
