#!/usr/bin/env python3
"""Validate the real COPS game-port Blowfish/Diffie-Hellman server challenge.

Read-only: do NOT transmit DH response, account token or gameplay packets.
The legacy cipher is implemented via libcrypto's deprecated BF_cfb64_* API
for interoperability testing; it is not a modern secure transport.
"""
import ctypes
import ctypes.util
import re
import socket
import struct

HOST="127.0.0.1"
GAME_PORT=5816
MAX_PROOF=4096
INITIAL_KEY=b"DR654dt34trg4UI6"
SERVER_SEAL=b"TQServer"

class BFKey(ctypes.Structure):
    _fields_=[("p",ctypes.c_uint32*18),("s",ctypes.c_uint32*1024)]

def crypto_library():
    path=ctypes.util.find_library("crypto")
    if not path:
        raise RuntimeError("OpenSSL libcrypto not available")
    lib=ctypes.CDLL(path)
    if not hasattr(lib,"BF_set_key") or not hasattr(lib,"BF_cfb64_encrypt"):
        raise RuntimeError("OpenSSL legacy Blowfish CFB64 symbols unavailable")
    lib.BF_set_key.argtypes=[ctypes.POINTER(BFKey),ctypes.c_int,ctypes.c_void_p]
    lib.BF_set_key.restype=None
    lib.BF_cfb64_encrypt.argtypes=[
        ctypes.c_void_p,ctypes.c_void_p,ctypes.c_long,
        ctypes.POINTER(BFKey),ctypes.c_void_p,ctypes.POINTER(ctypes.c_int),ctypes.c_int]
    lib.BF_cfb64_encrypt.restype=None
    return lib

def transform(data,key=INITIAL_KEY,iv=bytes(8),encrypt=False):
    """One fresh Blowfish CFB64 stream (OpenSSL wire interoperability only)."""
    if not key or len(key)>72:
        raise ValueError("Legacy COPS Blowfish supports keys of 1..72 bytes")
    if len(iv)!=8:
        raise ValueError("Blowfish IV must contain exactly 8 bytes")
    if not data:
        return b""
    lib=crypto_library()
    schedule=BFKey()
    source=ctypes.create_string_buffer(data,len(data))
    output=ctypes.create_string_buffer(len(data))
    seed=ctypes.create_string_buffer(key,len(key))
    iv_buffer=ctypes.create_string_buffer(iv,8)
    index=ctypes.c_int(0)
    lib.BF_set_key(ctypes.byref(schedule),len(key),seed)
    lib.BF_cfb64_encrypt(source,output,len(data),ctypes.byref(schedule),
                         iv_buffer,ctypes.byref(index),1 if encrypt else 0)
    return output.raw

def _i32(buf,pos):
    if pos<0 or pos+4>len(buf):
        raise ValueError("truncated proof length")
    return struct.unpack_from("<i",buf,pos)[0]

def _read_sized(buf,offset,max_length):
    length=_i32(buf,offset)
    start=offset+4
    if length<=0 or length>max_length or start+length>len(buf):
        raise ValueError("invalid or truncated DH proof field")
    return buf[start:start+length],start+length

def decode_proof(ciphertext):
    if len(ciphertext)<64 or len(ciphertext)>MAX_PROOF:
        raise ValueError("unexpected server challenge byte count")
    raw=transform(ciphertext)
    if _i32(raw,11)!=len(raw)-11:
        raise ValueError("advertised COPS DH message size mismatch")
    if raw[-8:]!=SERVER_SEAL:
        raise ValueError("incorrect server seal")
    data=raw[:-8]
    if _i32(data,15)!=12:
        raise ValueError("unexpected DH challenge junk field size")
    pos=19+12
    en_iv,pos=_read_sized(data,pos,8)
    de_iv,pos=_read_sized(data,pos,8)
    if len(en_iv)!=8 or len(de_iv)!=8:
        raise ValueError("DH challenge IV is not 8 bytes")
    pbytes,pos=_read_sized(data,pos,512)
    gbytes,pos=_read_sized(data,pos,16)
    abytes,pos=_read_sized(data,pos,512)
    if pos!=len(data):
        raise ValueError("unexpected trailing challenge bytes")
    for value in (pbytes,gbytes,abytes):
        if not re.fullmatch(rb"[0-9a-fA-F]+",value):
            raise ValueError("non-hexadecimal DH public parameter")
    modulus=int(pbytes,16)
    generator=int(gbytes,16)
    public=int(abytes,16)
    if modulus.bit_length()<256 or generator not in (2,5) or not (1<public<modulus-1):
        raise ValueError("implausible DH server public parameters")
    return {"p":pbytes,"g":gbytes,"a":abytes,"encrypt_iv":en_iv,"decrypt_iv":de_iv}

def read_server_challenge():
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(5)
        ciphertext=bytearray()
        expected=None
        while expected is None or len(ciphertext)<expected:
            part=sock.recv(MAX_PROOF-len(ciphertext))
            if not part:
                raise RuntimeError("game server closed before DH challenge completed")
            ciphertext.extend(part)
            if expected is None and len(ciphertext)>=15:
                header=transform(bytes(ciphertext[:15]))
                claimed=_i32(header,11)
                expected=11+claimed
                if expected<64 or expected>MAX_PROOF:
                    raise RuntimeError("invalid advertised game challenge size")
            if len(ciphertext)>MAX_PROOF:
                raise RuntimeError("game challenge exceeded size cap")
    if expected!=len(ciphertext):
        raise RuntimeError("game challenge contained unexpected extra bytes")
    return decode_proof(bytes(ciphertext)),len(ciphertext)

def probe():
    params,n=read_server_challenge()
    print("PASS: real COPS initial game challenge decrypted and structurally validated",flush=True)
    print("DH length: %d bytes; modulus: %d bits; generator: %s; public: %d hex chars"%
          (n,int(params["p"],16).bit_length(),params["g"].decode("ascii"),len(params["a"])),flush=True)
    print("No client DH response, token redemption, actual character login or world entry tested.",flush=True)

if __name__=="__main__":
    probe()
