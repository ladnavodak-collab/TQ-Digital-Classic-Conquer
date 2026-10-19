#!/usr/bin/env python3
"""Reject encrypted invalid DH-response sizes on a live loopback COPS server.

No DH key, account credentials, or successful game session is transmitted.
"""
import socket
import struct
import subprocess
import time

PORT=5816
INITIAL_KEY=b"DR654dt34trg4UI6"

def invalid_dh_prefix(declared_size):
    if not -(2**31)<=declared_size<2**31:
        raise ValueError("signed 32-bit value required")
    # COPS MsgLoginChallengeS starts with 7 padding bytes and a
    # 32-bit signed length encrypted under the initial Blowfish key.
    return bytes(7)+struct.pack("<i",declared_size)

def encrypt_prefix(payload):
    if len(payload)!=11:
        raise ValueError("exactly one COPS game handshake prefix required")
    p=subprocess.run(["openssl","enc","-bf-cfb","-e","-provider","default",
        "-provider","legacy","-K",INITIAL_KEY.hex(),
        "-iv","0000000000000000","-nosalt"],
        input=payload,capture_output=True,check=False)
    if p.returncode or len(p.stdout)!=len(payload):
        raise RuntimeError("OpenSSL Blowfish CFB encryption failed")
    return p.stdout

def send_invalid(declared):
    with socket.create_connection(("127.0.0.1",PORT),timeout=3) as sock:
        sock.settimeout(4)
        if not sock.recv(4096):
            raise RuntimeError("COPS did not send its initial DH challenge")
        sock.sendall(encrypt_prefix(invalid_dh_prefix(declared)))
        # A rejected handshake may close the connection or remain silent;
        # no authenticated or post-key-exchange response is permitted.
        sock.settimeout(1)
        try:
            received=sock.recv(256)
            if received:
                raise RuntimeError("Invalid DH length produced game response")
        except (ConnectionResetError,socket.timeout):
            pass

def probe():
    for invalid_length in (-1,0,4096,2**31-1):
        send_invalid(invalid_length)
        time.sleep(0.1)
    # Fresh game connection must still work after all rejection paths.
    with socket.create_connection(("127.0.0.1",PORT),timeout=3) as sock:
        sock.settimeout(3)
        if not sock.recv(4096):
            raise RuntimeError("COPS stopped producing DH challenges")
    print("PASS: real COPS survived 4 encrypted invalid DH-response length packets",flush=True)
    print("No valid game DH exchange, ticket redemption, character login or world entry claimed.",flush=True)

if __name__=="__main__":
    probe()
