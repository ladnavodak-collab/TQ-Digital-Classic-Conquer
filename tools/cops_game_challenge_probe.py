#!/usr/bin/env python3
"""Parse original COPS Blowfish-encrypted 1002 game-port DH challenge.

This test intentionally does not create or send a DH response.
"""
import re
import socket
import struct
import subprocess

MAX_CHALLENGE=4096
PORT=5816
def decode_structure(data):
    if len(data)<75 or len(data)>MAX_CHALLENGE:
        raise ValueError("DH challenge length outside bounds")
    if not data.endswith(b"TQServer"):
        raise ValueError("missing encrypted COPS server seal")
    end=len(data)-8
    pos=11
    def size():
        nonlocal pos
        if pos+4>end:raise ValueError("truncated DH size")
        (n,)=struct.unpack_from("<i",data,pos)
        pos+=4
        if n<0 or n>end-pos:raise ValueError("invalid DH component length")
        return n
    (declared,)=struct.unpack_from('<i',data,pos)
    pos+=4
    if declared != len(data)-11:
        raise ValueError("COPS challenge declared byte count mismatch")
    junk=size()
    if junk!=12:raise ValueError("unexpected COPS junk padding")
    pos+=junk
    en=size()
    if en!=8:raise ValueError("invalid outbound Blowfish IV")
    pos+=en
    de=size()
    if de!=8:raise ValueError("invalid inbound Blowfish IV")
    pos+=de
    numbers=[]
    for _ in range(3):
        n=size()
        if not 1<=n<=256:raise ValueError("oversized DH public value")
        value=data[pos:pos+n]
        pos+=n
        if not re.fullmatch(rb"[0-9A-Fa-f]+",value):
            raise ValueError("non-hexadecimal DH value")
        numbers.append(value)
    if pos != end:raise ValueError("unexpected trailing DH bytes")
    p,g,a=numbers
    if len(p)<64 or g!=b"05" or int(a,16)<=1 or int(a,16)>=int(p,16):
        raise ValueError("DH parameter validation failed")
    return {"encrypted_length":len(data),"p_hex_len":len(p),
            "g":g.decode(),"a_hex_len":len(a)}

def probe(helper):
    with socket.create_connection(("127.0.0.1",PORT),timeout=3) as sock:
        sock.settimeout(2)
        ciphertext=bytearray()
        while len(ciphertext)<MAX_CHALLENGE:
            try:
                chunk=sock.recv(MAX_CHALLENGE-len(ciphertext))
            except socket.timeout:
                break
            if not chunk:break
            ciphertext.extend(chunk)
            # Original server emits challenge in one write; allow further
            # fragments, then the 2-second idle timeout will end this read.
    if not ciphertext:raise RuntimeError("COPS did not emit game handshake")
    done=subprocess.run([helper],input=bytes(ciphertext),capture_output=True,check=True)
    data=decode_structure(done.stdout)
    print("PASS: real COPS Blowfish game challenge decrypted and validated",data,flush=True)
    print("Only the server's public DH values were inspected; no game login completed.",flush=True)

if __name__=="__main__":
    import sys
    if len(sys.argv)!=2:raise SystemExit("Usage: cops_game_challenge_probe.py <compiled Blowfish helper>")
    probe(sys.argv[1])
