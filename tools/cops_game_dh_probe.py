#!/usr/bin/env python3
"""Read and validate the actual COPS pre-login Blowfish/DH server challenge.

This is a localhost-only diagnostic; it does NOT send a DH response.
"""
import socket
import struct
import subprocess
import sys

INITIAL_GAME_KEY=b"DR654dt34trg4UI6"
PORT=5816

def decrypt_challenge(encrypted):
    if not 64 <= len(encrypted) <= 4096:
        raise ValueError("unexpected game challenge wire length")
    process=subprocess.run(
        ["openssl","enc","-bf-cfb","-d","-provider","default",
         "-provider","legacy","-K",INITIAL_GAME_KEY.hex(),"-iv","0000000000000000",
         "-nosalt"],
        input=encrypted,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if process.returncode:
        raise RuntimeError("OpenSSL Blowfish/CFB unavailable or failed")
    return process.stdout

def parse_challenge(plain):
    if len(plain)<60 or len(plain)>4096:
        raise ValueError("challenge is outside expected bounds")
    if not plain.endswith(b"TQServer"):
        raise ValueError("game challenge missing COPS server seal")
    declared=struct.unpack_from("<i",plain,11)[0]
    if declared != len(plain)-11:
        raise ValueError("declared COPS DH packet length disagrees with wire")
    index=15
    def read_i32():
        nonlocal index
        if index+4>len(plain)-8: raise ValueError("truncated challenge length")
        value=struct.unpack_from("<i",plain,index)[0]
        index+=4
        return value
    def read_part(limit):
        nonlocal index
        n=read_i32()
        if not 0<=n<=limit or index+n>len(plain)-8:
            raise ValueError("malformed DH challenge field size")
        part=plain[index:index+n]
        index+=n
        return part
    junk=read_part(64)
    if len(junk)!=12:raise ValueError("unexpected COPS game junk length")
    en_iv=read_part(8)
    de_iv=read_part(8)
    if len(en_iv)!=8 or len(de_iv)!=8:
        raise ValueError("bad Blowfish IV lengths")
    p=read_part(256)
    g=read_part(32)
    a=read_part(256)
    if index!=len(plain)-8:
        raise ValueError("trailing DH data before seal")
    try:
        pn=int(p.decode("ascii"),16)
        gn=int(g.decode("ascii"),16)
        an=int(a.decode("ascii"),16)
    except (ValueError,UnicodeError) as exc:
        raise ValueError("invalid DH hexadecimal public key") from exc
    if pn.bit_length()<256 or gn!=5 or not 1<an<pn:
        raise ValueError("invalid or unexpected COPS DH parameters")
    return {"size":len(plain),"dh_prime_bits":pn.bit_length(),
            "dh_generator":gn,"public_key_hex_length":len(a),
            "iv_bytes":len(en_iv)}

def probe():
    with socket.create_connection(("127.0.0.1",PORT),timeout=3) as sock:
        sock.settimeout(3)
        data=bytearray()
        while len(data)<4096:
            try:chunk=sock.recv(4096-len(data))
            except socket.timeout:break
            if not chunk:break
            data.extend(chunk)
            if len(data)>=333:break
    info=parse_challenge(decrypt_challenge(bytes(data)))
    print("PASS: real COPS game-port Blowfish/DH challenge decrypted and validated",info,flush=True)
    print("No DH response, transfer redemption, character entry or 5065 client is tested.",flush=True)

if __name__=="__main__":
    probe()
