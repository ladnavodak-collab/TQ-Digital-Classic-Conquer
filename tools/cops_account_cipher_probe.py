#!/usr/bin/env python3
"""Localhost-only encrypted COPS account packet negative-path integration probe.

Implements the *client-to-COPS* direction of upstream TqCipher::decrypt.
This deliberately sends a non-terminated account field, not credentials.
"""
import socket
import struct

ACCOUNT_PORT = 9958
P = 0x13FA0F9D
G = 0x6D5C7962
MSG_ACCOUNT = 1051

def initial_keys():
    p=bytearray(struct.pack("<I",P))
    g=bytearray(struct.pack("<I",G))
    key1=bytearray()
    key2=bytearray()
    for _ in range(256):
        key1.append(p[0])
        key2.append(g[0])
        p[0] = ((p[1] + ((p[0] * p[2]) & 255)) * p[0] + p[3]) & 255
        g[0] = ((g[1] - ((g[0] * g[2]) & 255)) * g[0] + g[3]) & 255
    return key1,key2

def swap_nibbles(byte):
    return ((byte << 4) | (byte >> 4)) & 255

def to_server(plaintext):
    """Inverse of original COPS TqCipher::decrypt for a fresh connection."""
    a,b=initial_keys()
    return bytes(swap_nibbles(c) ^ a[i & 255] ^ b[(i >> 8)&255] ^ 0xAB
                 for i,c in enumerate(plaintext))

def server_decrypt(ciphertext):
    """Mirror upstream server decrypt to independently check outbound bytes."""
    a,b=initial_keys()
    return bytes(swap_nibbles(c ^ 0xAB ^ a[i & 255] ^ b[(i >> 8)&255])
                 for i,c in enumerate(ciphertext))

def malformed_account_packet():
    # 4-byte packet header plus exactly three 16-byte account fields.
    # Absence of NUL in Account must trigger the patched MsgAccount guard.
    return struct.pack("<HH",52,MSG_ACCOUNT) + b"X"*16 + bytes(16) + bytes(16)

def probe():
    plaintext=malformed_account_packet()
    wire=to_server(plaintext)
    if server_decrypt(wire)!=plaintext:
        raise RuntimeError("account cipher self-check failed")
    with socket.create_connection(("127.0.0.1",ACCOUNT_PORT),timeout=3) as sock:
        sock.settimeout(3)
        sock.sendall(wire)
        try:
            received=sock.recv(256)
        except ConnectionResetError:
            received=b""
        if received:
            raise RuntimeError("Malformed account packet unexpectedly generated a response")
    # The server must still accept new clients after malformed input.
    with socket.create_connection(("127.0.0.1",ACCOUNT_PORT),timeout=2):
        pass
    print("PASS: real COPS account port processed an encrypted, invalid-name packet without a reply and remained available",flush=True)
    print("This is a negative-path parser test, not successful account authentication.",flush=True)

if __name__=="__main__":
    probe()
