#!/usr/bin/env python3
"""Exercise a real COPS account-port login and encrypted transfer response."""
import argparse
import ctypes
import ctypes.util
import socket
import struct
import subprocess
import time
from cops_account_cipher_probe import ACCOUNT_PORT, MSG_ACCOUNT, initial_keys, swap_nibbles, to_server

ACCOUNT_ID=78
ACCOUNT_NAME="ci_auth"
PASSWORD="CiTestPass123"
SERVER_NAME="TQ-CI"
MASK=0xffffffff
RC5_SEED=bytes.fromhex("3cdcfee8c454d67e16a6f81ae8d038be")

def rotl(v,n):
    n=n&31
    return ((v<<n)|(v>>((32-n)&31)))&MASK

def rc5_password(payload):
    if len(payload)!=16:raise ValueError("expected 16-byte password field")
    keys=list(struct.unpack("<4I",RC5_SEED))
    sub=[0]*26
    sub[0]=0xB7E15163
    for i in range(1,26):sub[i]=(sub[i-1]-0x61C88647)&MASK
    x=y=i=j=0
    for _ in range(3*max(len(keys),len(sub))):
        sub[i]=rotl((sub[i]+x+y)&MASK,3)
        x=sub[i];i=(i+1)%len(sub)
        keys[j]=rotl((keys[j]+x+y)&MASK,(x+y)&MASK)
        y=keys[j];j=(j+1)%len(keys)
    result=bytearray()
    for a,b in struct.iter_unpack("<II",payload):
        left=(a+sub[0])&MASK
        right=(b+sub[1])&MASK
        # Invert upstream RC5::decrypt, which iterates rounds 12 down to 1.
        # Upstream RC5::encrypt incorrectly stops at 11; don't mimic that bug.
        for r in range(1,13):
            left=(rotl(left^right,right)+sub[2*r])&MASK
            right=(rotl(right^left,left)+sub[2*r+1])&MASK
        result+=struct.pack("<II",left,right)
    return bytes(result)

def field(s):
    value=s.encode("ascii")
    if not 1<=len(value)<=15:raise ValueError("invalid legacy account field")
    return value.ljust(16,b"\0")

def request_packet(password=PASSWORD):
    return struct.pack("<HH",52,MSG_ACCOUNT)+field(ACCOUNT_NAME)+rc5_password(field(password))+field(SERVER_NAME)

def decode_response(wire):
    key1,key2=initial_keys()
    return bytes(swap_nibbles(c ^ key1[i&255] ^ key2[(i>>8)&255]) ^ 0xAB
                 for i,c in enumerate(wire))

def hash_password():
    path=ctypes.util.find_library("sodium")
    if not path:raise RuntimeError("libsodium unavailable")
    lib=ctypes.CDLL(path)
    lib.sodium_init.restype=ctypes.c_int
    if lib.sodium_init()<0:raise RuntimeError("libsodium init failed")
    lib.crypto_pwhash_opslimit_interactive.restype=ctypes.c_ulonglong
    lib.crypto_pwhash_memlimit_interactive.restype=ctypes.c_size_t
    lib.crypto_pwhash_str.restype=ctypes.c_int
    lib.crypto_pwhash_str.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_ulonglong,ctypes.c_ulonglong,ctypes.c_size_t]
    out=ctypes.create_string_buffer(128)
    pw=PASSWORD.encode("ascii")
    code=lib.crypto_pwhash_str(out,pw,len(pw),lib.crypto_pwhash_opslimit_interactive(),lib.crypto_pwhash_memlimit_interactive())
    if code!=0:raise RuntimeError("libsodium password hashing failed")
    encoded=out.value.decode("ascii")
    if not encoded.startswith("$argon2id$"):raise RuntimeError("not Argon2id")
    return encoded

def seed(cli):
    encoded=hash_password()
    query=("INSERT INTO `account` (`id`,`name`,`password`) VALUES "
           "(%d,'%s','%s')"%(ACCOUNT_ID,ACCOUNT_NAME,encoded))
    result=subprocess.run(cli+["--execute",query],capture_output=True,text=True)
    if result.returncode:raise RuntimeError("disposable account INSERT failed: "+result.stderr[-250:])
    print("PASS: fresh Argon2id account fixture written to disposable MariaDB",flush=True)

def probe():
    with socket.create_connection(("127.0.0.1",ACCOUNT_PORT),timeout=3) as sock:
        sock.settimeout(5)
        sock.sendall(to_server(request_packet()))
        wire=bytearray()
        while len(wire)<40:
            data=sock.recv(128)
            if not data:break
            wire.extend(data)
    if len(wire)<32:raise RuntimeError("COPS sent no account authentication response")
    result=decode_response(wire)
    length,typ,uid,token,ip,port=struct.unpack_from("<HHii16sI",result)
    if (length,typ,uid,port)!=(32,1055,ACCOUNT_ID,5816):
        raise RuntimeError("Unexpected response fields: "+str((length,typ,uid,port)))
    if token<10000:raise RuntimeError("No valid issued account-game ticket")
    if ip.split(b"\0",1)[0]!=b"127.0.0.1":raise RuntimeError("Nonloopback redirect rejected")
    print("PASS: real COPS authenticated an Argon2id test account and returned an encrypted transfer ticket",flush=True)
    print("PASS: account ID, loopback game port and positive ticket decoded (ticket not logged)",flush=True)
    print("No game-port DH, ticket redemption, 5065 client or character entry is asserted.",flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=("seed","probe"))
    ap.add_argument("mysql",nargs="*")
    a=ap.parse_args()
    if a.action=="seed":
        if not a.mysql:ap.error("seed requires MariaDB CLI command")
        seed(a.mysql)
    else:probe()
